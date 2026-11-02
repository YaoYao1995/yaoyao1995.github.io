"""Offline regression checks for the citation refresh HTTP/validation boundary."""
import copy
from contextlib import ExitStack
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import re
import traceback
import unittest
from unittest.mock import Mock, mock_open, patch
import urllib.error
import urllib.request


MODULE_PATH = Path(__file__).with_name("main.py")
SPEC = importlib.util.spec_from_file_location("citation_refresh", MODULE_PATH)
main = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(main)
SCHOLAR_ID = "hNO0NdEAAAAJ"
URL = "https://scholar.google.com/citations?user=" + SCHOLAR_ID


def profile_html(*, more=False, publication_id=None):
    pid = publication_id or SCHOLAR_ID + ":paper001"
    metrics = "".join(
        '<td class="gsc_rsb_std">' + value + "</td>"
        for value in ("1,234", "987", "12", "10", "18", "15")
    )
    return """<html><body>
      <div id="gsc_prf_in">Yao Yao</div>
      <table id="gsc_rsb_st"><tr>{metrics}</tr></table>
      <table><tbody id="gsc_a_b"><tr class="gsc_a_tr">
        <td class="gsc_a_t">
          <a class="gsc_a_at" href="/citations?view_op=view_citation&amp;citation_for_view={pid}">Flood forecasting</a>
          <div class="gs_gray">Yao Yao, A Researcher</div>
          <div class="gs_gray">Journal of Hydrology, 2026</div>
        </td>
        <td class="gsc_a_c"><a class="gsc_a_ac" href="/scholar?cites=12345">42</a></td>
        <td class="gsc_a_y"><span>2026</span></td>
      </tr></tbody></table>
      <button id="gsc_bpf_more" {disabled}>Show more</button>
    </body></html>""".format(metrics=metrics, pid=pid, disabled="" if more else "disabled")


def opener_for(html):
    def opener(request, timeout):
        response = io.BytesIO(html if isinstance(html, bytes) else html.encode("utf-8"))
        response.status = 200
        return response
    return Mock(side_effect=opener)


def profile_page(start, count, *, more=False):
    html = profile_html(more=more)
    row = re.search(r'<tr class="gsc_a_tr">.*?</tr>', html, re.S).group()
    rows = "".join(row.replace("paper001", "paper" + str(start + index).zfill(4))
                   for index in range(count))
    return html.replace(row, rows)


def page_sequence_opener(pages):
    remaining = iter(pages)

    def opener(request, timeout):
        response = io.BytesIO(next(remaining).encode("utf-8"))
        response.status = 200
        return response
    return Mock(side_effect=opener)


def requested_offsets(opener):
    return [int(urllib.parse.parse_qs(urllib.parse.urlparse(call.args[0].full_url).query)["cstart"][0])
            for call in opener.call_args_list]


class ScholarValidationTests(unittest.TestCase):
    def test_complete_profile_has_six_metrics_and_expected_publication_identity(self):
        parsed = main.parse_page(profile_html(), SCHOLAR_ID)
        self.assertEqual(parsed["name"], "Yao Yao")
        self.assertEqual(parsed["metrics"], dict(
            citedby=1234, citedby5y=987, hindex=12, hindex5y=10,
            i10index=18, i10index5y=15,
        ))
        self.assertFalse(parsed["has_more"])
        pub = parsed["publications"][SCHOLAR_ID + ":paper001"]
        self.assertEqual(pub["author_pub_id"], SCHOLAR_ID + ":paper001")
        self.assertEqual(pub["bib"]["title"], "Flood forecasting")
        self.assertEqual(pub["num_citations"], 42)
        self.assertEqual(pub["cites_id"], ["12345"])

    def test_successful_fetch_preserves_input_snapshot(self):
        previous = {"updated": "2026-10-29T00:00:00Z", "citedby": 1200,
                    "publications": {SCHOLAR_ID + ":paper001": {"num_citations": 40}}}
        before = copy.deepcopy(previous)
        result = main.fetch_scholar(SCHOLAR_ID, previous,
                                    opener=opener_for(profile_html()), sleeper=Mock())
        self.assertEqual(result["scholar_id"], SCHOLAR_ID)
        self.assertEqual(result["citedby"], 1234)
        self.assertEqual(previous, before)
        self.assertNotEqual(result["updated"], previous["updated"])

    def test_http_200_challenge_is_rejected(self):
        challenge = '<html><form action="/sorry/index"><div id="recaptcha"></div></form></html>'
        with self.assertRaisesRegex(main.ScholarFetchError, "access challenge"):
            main.fetch_scholar(SCHOLAR_ID, opener=opener_for(challenge), sleeper=Mock())

    def test_http_403_is_not_retried_or_allowed_to_mutate_previous_snapshot(self):
        previous = {"updated": "2026-10-29T00:00:00Z", "citedby": 546,
                    "publications": {SCHOLAR_ID + ":paper001": {"bib": {"title": "Old title"}}}}
        before = copy.deepcopy(previous)
        opener = Mock(side_effect=urllib.error.HTTPError(URL, 403, "Forbidden", {}, None))
        sleeper = Mock()
        with self.assertRaisesRegex(main.ScholarFetchError, "HTTP 403"):
            main.fetch_scholar(SCHOLAR_ID, previous, opener=opener, sleeper=sleeper)
        opener.assert_called_once()
        sleeper.assert_not_called()
        self.assertEqual(previous, before)

    def test_foreign_publication_id_is_rejected(self):
        with self.assertRaisesRegex(main.ScholarFetchError, "foreign"):
            main.parse_page(profile_html(publication_id="someoneElse:paper001"), SCHOLAR_ID)

    def test_truncated_page_cannot_be_published_as_complete(self):
        with self.assertRaisesRegex(main.ScholarFetchError, "Truncated Scholar page"):
            main.fetch_scholar(SCHOLAR_ID, opener=opener_for(profile_html(more=True)), sleeper=Mock())

    def test_html_bytes_allow_windows_1252_titles(self):
        html = profile_html().replace("<html>", '<html><head><meta charset="windows-1252"></head>')
        html = html.replace("Flood forecasting", "Flood–risk forecasting")
        body = html.encode("windows-1252")
        received = main._profile_html(URL, opener_for(body), Mock())
        self.assertIsInstance(received, bytes)
        parsed = main.parse_page(received, SCHOLAR_ID)
        self.assertEqual(parsed["publications"][SCHOLAR_ID + ":paper001"]["bib"]["title"],
                         "Flood–risk forecasting")


class ScholarPaginationTests(unittest.TestCase):
    def test_complete_profiles_across_page_boundaries(self):
        for total in (100, 101, 200, 201, 300):
            with self.subTest(total=total):
                offsets = list(range(0, total, 100))
                pages = [profile_page(start, min(100, total - start), more=start + 100 < total)
                         for start in offsets]
                opener = page_sequence_opener(pages)
                result = main.fetch_scholar(SCHOLAR_ID, opener=opener, sleeper=Mock())
                self.assertEqual(len(result["publications"]), total)
                self.assertEqual(result["scholar_id"], SCHOLAR_ID)
                self.assertEqual(requested_offsets(opener), offsets)
                self.assertIn(SCHOLAR_ID + ":paper" + str(total - 1).zfill(4),
                              result["publications"])

    def test_exact_page_totals_allow_an_explicit_empty_terminal_page(self):
        for total in (100, 200):
            with self.subTest(total=total):
                pages = [profile_page(start, 100, more=True) for start in range(0, total, 100)]
                pages.append(profile_page(total, 0))
                opener = page_sequence_opener(pages)
                result = main.fetch_scholar(SCHOLAR_ID, opener=opener, sleeper=Mock())
                self.assertEqual(len(result["publications"]), total)
                self.assertEqual(requested_offsets(opener), list(range(0, total + 1, 100)))

    def test_first_page_must_not_be_empty(self):
        opener = page_sequence_opener([profile_page(0, 0)])
        with self.assertRaises(main.ScholarFetchError):
            main.fetch_scholar(SCHOLAR_ID, opener=opener, sleeper=Mock())
        self.assertEqual(requested_offsets(opener), [0])

    def test_empty_later_page_with_more_enabled_is_rejected(self):
        opener = page_sequence_opener([profile_page(0, 100, more=True),
                                       profile_page(100, 0, more=True)])
        with self.assertRaises(main.ScholarFetchError):
            main.fetch_scholar(SCHOLAR_ID, opener=opener, sleeper=Mock())
        self.assertEqual(requested_offsets(opener), [0, 100])

    def test_empty_terminal_page_cannot_hide_a_missing_previous_tail(self):
        previous = {"updated": "2026-10-29T00:00:00Z", "citedby": 546,
                    "publications": {
                        SCHOLAR_ID + ":paper" + str(index).zfill(4): {
                            "bib": {"title": "Previous publication"}, "num_citations": 1,
                        } for index in range(201)
                    }}
        before = copy.deepcopy(previous)
        opener = page_sequence_opener([profile_page(0, 100, more=True),
                                       profile_page(100, 100, more=True),
                                       profile_page(200, 0)])
        with self.assertRaises(main.ScholarFetchError):
            main.fetch_scholar(SCHOLAR_ID, previous, opener=opener, sleeper=Mock())
        self.assertEqual(requested_offsets(opener), [0, 100, 200])
        self.assertEqual(previous, before)

    def test_repeated_second_page_ids_are_rejected(self):
        opener = page_sequence_opener([profile_page(0, 100, more=True), profile_page(0, 100)])
        with self.assertRaisesRegex(main.ScholarFetchError, "Repeated Scholar pagination"):
            main.fetch_scholar(SCHOLAR_ID, opener=opener, sleeper=Mock())
        self.assertEqual(requested_offsets(opener), [0, 100])


class SerpApiTransportTests(unittest.TestCase):
    secret = "offline-test-secret-never-log"

    def test_scholar_request_maps_author_and_page_offset_to_fixed_api_endpoint(self):
        for start in (0, 100):
            with self.subTest(start=start):
                response = opener_for(profile_html())(None, 20)
                request = urllib.request.Request(URL + "&cstart=" + str(start))
                with patch.dict(main.os.environ, {"SERPAPI_KEY": self.secret}), \
                     patch.object(main.urllib.request, "urlopen", return_value=response) as opener:
                    with main._serpapi_open(request, timeout=17) as opened:
                        self.assertIn(b"Flood forecasting", opened.read())
                self.assertTrue(response.closed)
                args, kwargs = opener.call_args
                target = urllib.parse.urlparse(args[0].full_url)
                self.assertEqual((target.scheme, target.netloc, target.path),
                                 ("https", "serpapi.com", "/search"))
                self.assertEqual(urllib.parse.parse_qs(target.query), {
                    "engine": ["google_scholar_author"], "author_id": [SCHOLAR_ID],
                    "hl": ["en"], "num": ["100"], "start": [str(start)],
                    "output": ["html"], "api_key": [self.secret],
                })
                self.assertEqual(kwargs["timeout"], 60)

    def test_invalid_key_http_error_never_exposes_authenticated_url(self):
        sensitive_url = "https://serpapi.com/search?api_key=" + self.secret
        error_body = io.BytesIO(b'{"error":"invalid key"}')
        original = urllib.error.HTTPError(sensitive_url, 401, sensitive_url, {}, error_body)
        with patch.dict(main.os.environ, {"SERPAPI_KEY": self.secret}), \
             patch.object(main.urllib.request, "urlopen", side_effect=original):
            with self.assertRaises(main.ScholarFetchError) as caught:
                main._profile_html(URL, main._serpapi_open, Mock())
        output = "".join(traceback.format_exception(caught.exception))
        self.assertNotIn(self.secret, output)
        self.assertNotIn("api_key=", output)
        self.assertIn("HTTP 401", output)
        self.assertTrue(error_body.closed)

    def test_network_error_is_sanitized_before_retry_failure(self):
        original = urllib.error.URLError("failed: https://serpapi.com/search?api_key=" + self.secret)
        sleeper = Mock()
        with patch.dict(main.os.environ, {"SERPAPI_KEY": self.secret}), \
             patch.object(main.urllib.request, "urlopen", side_effect=original) as opener:
            with self.assertRaises(main.ScholarFetchError) as caught:
                main._profile_html(URL, main._serpapi_open, sleeper)
        output = "".join(traceback.format_exception(caught.exception))
        self.assertNotIn(self.secret, output)
        self.assertNotIn("api_key=", output)
        self.assertEqual(opener.call_count, 3)
        self.assertEqual(sleeper.call_count, 2)

    def test_json_error_with_http_200_cannot_pass_profile_validation(self):
        response = opener_for('{"error":"provider did not retrieve a profile"}')(None, 20)
        with patch.dict(main.os.environ, {"SERPAPI_KEY": self.secret}), \
             patch.object(main.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(main.ScholarFetchError, "Incomplete Scholar profile"):
                main.fetch_scholar(SCHOLAR_ID, opener=main._serpapi_open, sleeper=Mock())


class MainRoutingTests(unittest.TestCase):
    def run_refresh(self, *, key=None, metadata_only=False):
        previous = {
            "scholar_id": SCHOLAR_ID, "citedby": 546,
            "updated": "2026-10-29T00:00:00Z", "catalog_schema": 1,
            "publications": {SCHOLAR_ID + ":paper001": {
                "bib": {"title": "Flood forecasting"}, "num_citations": 42,
            }},
            "verified_publications": {SCHOLAR_ID + ":paper001": {"title": "Flood forecasting"}},
            "citation_provenance": {"upstream": "Google Scholar", "transport": "previous"},
        }
        env = {"GITHUB_REPOSITORY": "owner/site", "GOOGLE_SCHOLAR_ID": SCHOLAR_ID,
               "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_EVENT_PATH": "offline-event.json"}
        if key is not None:
            env["SERPAPI_KEY"] = key
        event = json.dumps({"inputs": {"metadata_only": str(metadata_only).lower()}})
        with ExitStack() as stack:
            stack.enter_context(patch.dict(main.os.environ, env, clear=True))
            stack.enter_context(patch("builtins.open", mock_open(read_data=event)))
            stack.enter_context(patch.object(main, "get_json", return_value=previous))
            fetch = stack.enter_context(patch.object(main, "fetch_scholar", return_value=copy.deepcopy(previous)))
            stack.enter_context(patch.object(main, "enrich"))
            stack.enter_context(patch("shutil.rmtree"))
            stack.enter_context(patch("os.makedirs"))
            stack.enter_context(patch("signal.signal"))
            stack.enter_context(patch("signal.alarm"))
            writes = stack.enter_context(patch("pathlib.Path.write_text"))
            stack.enter_context(patch("pathlib.Path.replace"))
            main.main()
        snapshot = json.loads(writes.call_args_list[0].args[0])
        return previous, fetch, snapshot

    def test_no_key_preserves_direct_transport(self):
        previous, fetch, snapshot = self.run_refresh()
        self.assertIs(fetch.call_args.kwargs["opener"], urllib.request.urlopen)
        self.assertEqual(snapshot["citation_provenance"]["transport"], "direct")
        self.assertEqual(snapshot["citation_provenance"]["upstream"], "Google Scholar")
        self.assertEqual(previous["updated"], "2026-10-29T00:00:00Z")

    def test_key_selects_serpapi_without_publishing_credentials(self):
        previous, fetch, snapshot = self.run_refresh(key="test-private-key")
        self.assertIs(fetch.call_args.kwargs["opener"], main._serpapi_open)
        self.assertEqual(snapshot["citation_provenance"]["transport"], "SerpApi")
        self.assertEqual(snapshot["citation_provenance"]["retrieved_at"], snapshot["updated"])
        self.assertNotIn("test-private-key", json.dumps(snapshot))
        self.assertEqual(previous["citation_provenance"]["transport"], "previous")

    def test_metadata_only_never_refetches_or_claims_new_scholar_update(self):
        previous, fetch, snapshot = self.run_refresh(key="test-private-key", metadata_only=True)
        fetch.assert_not_called()
        self.assertEqual(snapshot["updated"], previous["updated"])
        self.assertEqual(snapshot["citation_provenance"], previous["citation_provenance"])
        self.assertIn("catalog_updated", snapshot)


class CurrentWeekTests(unittest.TestCase):
    def test_china_monday_boundary_starts_new_week_at_sunday_1600_utc(self):
        now = datetime(2026, 11, 1, 16, 0, tzinfo=timezone.utc)
        self.assertFalse(main.current_week("2026-11-01T15:59:59Z", now))
        self.assertTrue(main.current_week("2026-11-01T16:00:00Z", now))

    def test_current_week_snapshot_skips_but_future_timestamp_does_not(self):
        now = datetime(2026, 11, 3, 0, 17, tzinfo=timezone.utc)
        self.assertTrue(main.current_week("2026-11-02T00:17:00Z", now))
        self.assertFalse(main.current_week("2026-11-03T00:18:00Z", now))
        self.assertFalse(main.current_week("not-a-timestamp", now))


if __name__ == "__main__":
    unittest.main()
