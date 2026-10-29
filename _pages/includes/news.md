# 🔥 News

<div id="scholar-news" aria-live="polite">
  <p>Loading research updates from <a href="https://scholar.google.com/citations?user=hNO0NdEAAAAJ&sortby=pubdate">Google Scholar</a>…</p>
</div>
<noscript><p>See my <a href="https://scholar.google.com/citations?user=hNO0NdEAAAAJ&sortby=pubdate">latest research on Google Scholar</a>.</p></noscript>

<script>
(function () {
  'use strict';
  // The daily Get Citation Data workflow refreshes this file.
  // Scholar supplies years, not acceptance dates: never infer acceptance or a venue.
  var root = document.getElementById('scholar-news');
  var scholarId = 'hNO0NdEAAAAJ';
  var source = 'https://raw.githubusercontent.com/YaoYao1995/yaoyao1995.github.io/google-scholar-stats/gs_data.json';
  var controller = new AbortController();
  var timer = setTimeout(function () { controller.abort(); }, 15000);

  fetch(source, { cache: 'no-store', signal: controller.signal })
    .then(function (response) {
      if (!response.ok) throw new Error('Scholar data unavailable');
      return response.json();
    })
    .then(function (data) {
      if (data.scholar_id !== scholarId || !data.publications) {
        throw new Error('Unexpected Scholar profile');
      }
      var byTitle = new Map();
      Object.keys(data.publications).forEach(function (id) {
        var bib = data.publications[id].bib || {};
        var title = typeof bib.title === 'string' ? bib.title.trim() : '';
        var yearText = String(bib.pub_year || '');
        if (!title || !/^\d{4}$/.test(yearText) || id.indexOf(scholarId + ':') !== 0) return;
        var year = Number(yearText);
        if (year < 1900 || year > new Date().getFullYear() + 1) return;
        // Merge duplicate title records, keeping the most recent listed year.
        var key = title.toLocaleLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
        var previous = byTitle.get(key);
        if (!previous || year > previous.year) byTitle.set(key, { id: id, title: title, year: year });
      });
      var groups = {};
      byTitle.forEach(function (item) {
        (groups[item.year] || (groups[item.year] = [])).push(item);
      });
      var years = Object.keys(groups).sort(function (a, b) { return Number(b) - Number(a); });
      if (!years.length) throw new Error('No dated research updates');
      var fragment = document.createDocumentFragment();
      years.forEach(function (year, index) {
        var section = document.createElement('details');
        section.open = index === 0;
        section.style.marginBottom = '0.8em';
        var heading = document.createElement('summary');
        heading.style.cursor = 'pointer';
        heading.style.fontWeight = '600';
        heading.textContent = year + ' · ' + groups[year].length + ' research updates';
        section.appendChild(heading);
        var list = document.createElement('ul');
        // Alphabetical within a year: Scholar does not supply reliable month/day dates.
        groups[year].sort(function (a, b) { return a.title.localeCompare(b.title); });
        groups[year].forEach(function (item) {
          var entry = document.createElement('li');
          entry.appendChild(document.createTextNode('🥳 Delighted to share our work: “'));
          var link = document.createElement('a');
          link.href = 'https://scholar.google.com/citations?view_op=view_citation&hl=en&user=' + scholarId + '&citation_for_view=' + encodeURIComponent(item.id);
          link.textContent = item.title;
          entry.appendChild(link);
          entry.appendChild(document.createTextNode('”!'));
          list.appendChild(entry);
        });
        section.appendChild(list);
        fragment.appendChild(section);
      });
      var note = document.createElement('p');
      note.style.fontSize = '0.8em';
      note.style.color = '#777';
      var updated = String(data.updated || '').match(/^\d{4}-\d{2}-\d{2}/);
      note.textContent = 'From Google Scholar · Grouped by listed publication year' + (updated ? ' · Updated ' + updated[0] : '');
      fragment.appendChild(note);
      root.replaceChildren(fragment);
    })
    .catch(function () {
      root.replaceChildren();
      var message = document.createElement('p');
      message.appendChild(document.createTextNode('Research updates are temporarily unavailable. '));
      var link = document.createElement('a');
      link.href = 'https://scholar.google.com/citations?user=' + scholarId + '&sortby=pubdate';
      link.textContent = 'View my latest work on Google Scholar.';
      message.appendChild(link);
      root.appendChild(message);
    })
    .finally(function () { clearTimeout(timer); });
})();
</script>
