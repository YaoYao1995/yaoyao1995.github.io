<style style="display:none !important">
.scholar-section{max-width:920px;margin:48px 0;color:#39474c;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;scroll-margin-top:90px}
.scholar-section .scholar-heading{font-family:Georgia,"Times New Roman",serif;font-size:32px;font-weight:400;letter-spacing:-.025em;line-height:1.2;margin:0 0 10px;border:0;padding:0;color:#213c43}
.scholar-section .scholar-subtitle,.scholar-section .scholar-note{font-size:12px;line-height:1.65;color:#65767b;margin:0 0 22px}
.scholar-section a{color:#286570;text-decoration:none;border-bottom:1px solid transparent;overflow-wrap:anywhere}
.scholar-section a:hover{border-bottom-color:#8baeb4;color:#173d45}
.scholar-section a:focus-visible,.scholar-section summary:focus-visible{outline:2px solid #286570;outline-offset:4px}
.scholar-section details{border-top:1px solid #dae4e5}
.scholar-section summary{cursor:pointer;padding:16px 0;font-size:17px;font-weight:500;color:#2c4b53;font-variant-numeric:tabular-nums}
.scholar-section summary .year-count{font-size:11px;font-weight:400;color:#75848a;margin-left:12px}
.scholar-section .scholar-list{list-style:none;padding:0;margin:0 0 20px}
.scholar-section .scholar-list li{margin:0;padding:14px 0;border-top:1px solid #edf1f2;min-width:0}
.scholar-section .news-line{font-size:14px;line-height:1.8;margin:0;overflow-wrap:anywhere}
.scholar-section .news-line a{font-weight:500}
.scholar-section .paper-title{font-size:16px;font-weight:500;line-height:1.55;margin:0 0 7px;overflow-wrap:anywhere}
.scholar-section .paper-authors{font-size:12px;line-height:1.6;color:#758087;margin:0 0 8px;overflow-wrap:anywhere}
.scholar-section .paper-authors strong{font-weight:600;color:#3d5961}
.scholar-section .paper-meta{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline;font-size:12px;line-height:1.6;margin:6px 0 0;color:#65767b}
.scholar-section .paper-venue{font-weight:600;color:#286570}
.scholar-section .scholar-note{margin-top:16px}
.scholar-section .citation-badge{display:inline-flex;align-items:stretch;vertical-align:middle;border:0;border-radius:4px;overflow:hidden;font-size:12px;line-height:22px;font-weight:400;white-space:nowrap;color:#333;text-decoration:none;margin:2px 0}
.scholar-section .citation-badge:hover{border:0;filter:brightness(.96)}
.scholar-section .citation-label{display:inline-flex;align-items:center;gap:5px;padding:0 6px;background:#e2e2e2}
.scholar-section .citation-label svg{width:15px;height:15px;fill:#4285f4;flex:none}
.scholar-section .citation-value{padding:0 6px;background:#91c2ee;color:#333;font-variant-numeric:tabular-nums}
.scholar-section #scholar-total{display:inline-block;margin-left:7px}
@media(max-width:700px){.scholar-section{margin:34px 0}.scholar-section .scholar-heading{font-size:28px}.scholar-section .paper-title{font-size:15px}.scholar-section summary{padding:14px 0}.scholar-section .paper-meta{gap:5px 10px}.scholar-section .scholar-list li{padding:13px 0}}
</style>
<section class="scholar-section" id="-news" aria-labelledby="news-heading">
<h2 class="scholar-heading" id="news-heading">News</h2>
<p class="scholar-subtitle">New publications &amp; research milestones</p>
<div id="scholar-news" aria-live="polite"><p class="scholar-note">Loading publication updates…</p></div>
</section>
<section class="scholar-section" id="-publications-categorized-by-research-area" aria-labelledby="publications-heading">
<h2 class="scholar-heading" id="publications-heading">Publications</h2>
<p class="scholar-subtitle">Journal articles &amp; selected conference papers · <a href="https://scholar.google.com/citations?user=hNO0NdEAAAAJ">Google Scholar ↗</a> <span id="scholar-total"></span></p>
<div id="formal-publications" aria-live="polite"><p class="scholar-note">Loading publications…</p></div>
</section>
<noscript><p>View my publications on <a href="https://scholar.google.com/citations?user=hNO0NdEAAAAJ">Google Scholar</a>.</p></noscript>
<script>
(function(){
'use strict';
var scholarId='hNO0NdEAAAAJ';
var roots=[document.getElementById('scholar-news'),document.getElementById('formal-publications')];
var newsTemplates=[['🥳 Delighted to share our work: ','!'],['🎉 Excited to introduce ','!'],['✨ A research highlight to share: ','.'],['📚 From our research collection: ','.'],['🥳 Happy to put the spotlight on ','!'],['🔎 Take a closer look at ','.'],['🎊 Celebrating the work behind ','!'],['💡 Explore the ideas in ','.'],['📖 A contribution we are pleased to share: ','.'],['🙌 Proud to share ',' with you!'],['✨ In the research spotlight: ','.'],['🎉 Here is a piece of our research journey: ','!'],['🔬 Discover our work on ','.'],['🥳 A little research celebration for ','!'],['📚 On our reading list: ','.'],['💬 We would love to hear your thoughts on ','.'],['🌟 Highlighting a contribution from our team: ','.'],['🎊 A moment to celebrate ','!'],['💡 Curious about our research? Explore ','.'],['📖 For a closer look at our work, read ','.'],['🙌 Sharing a chapter of our research story: ','.'],['✨ An invitation to explore ','.'],['🔎 Behind this title is a research journey: ','.'],['🎉 Pleased to bring you ','!'],['🥳 Here is some research worth sharing: ','!']];
var bag=[],last=-1;
function nextNewsTemplate(){if(!bag.length){bag=newsTemplates.map(function(_,i){return i;});for(var i=bag.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=bag[i];bag[i]=bag[j];bag[j]=t;}if(bag[bag.length-1]===last){var t=bag[0];bag[0]=bag[bag.length-1];bag[bag.length-1]=t;}}last=bag.pop();return newsTemplates[last];}
function el(tag,cls,text){var node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node;}
function safeLink(url){try{var u=new URL(url);return u.protocol==='https:'&&!/arxiv|ssrn|patents|biorxiv|medrxiv|researchsquare|techrxiv/i.test(u.hostname);}catch(e){return false;}}
function citationBadge(count){var link=el('a','citation-badge');link.setAttribute('aria-label',count+' citations on Google Scholar');var label=el('span','citation-label');var icon=document.createElementNS('http://www.w3.org/2000/svg','svg');icon.setAttribute('viewBox','0 0 24 24');icon.setAttribute('aria-hidden','true');var path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d','M12 1 0 10l4.8 3.6A8 8 0 0 1 12 9a8 8 0 0 1 7.2 4.6L24 10 12 1zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14z');icon.appendChild(path);label.appendChild(icon);label.appendChild(document.createTextNode('citations'));link.appendChild(label);link.appendChild(el('span','citation-value',String(count)));return link;}
function metadata(p){var row=el('p','paper-meta');var venue=el('span','paper-venue',p.venue_short||p.venue);venue.title=p.venue;row.appendChild(venue);row.appendChild(el('span','',String(p.year)));row.appendChild(el('span','',p.kind==='journal'?'Journal article':'Conference paper'));return row;}
function authorLine(names){var line=el('p','paper-authors');String(names||'').split(/(Yao Yao)/i).forEach(function(part){line.appendChild(part.toLowerCase()==='yao yao'?el('strong','',part):document.createTextNode(part));});return line;}
function render(data){
 if(data.scholar_id!==scholarId||data.catalog_schema!==1||!data.verified_publications)throw new Error('Verified catalog unavailable');
 var seen=new Set(),groups={};
 Object.values(data.verified_publications).forEach(function(p){
  if(!p.title||!p.venue||!['journal','conference'].includes(p.kind)||!Number.isInteger(p.year)||!safeLink(p.url))return;
  var key=p.url.toLowerCase();if(seen.has(key))return;seen.add(key);(groups[p.year]||(groups[p.year]=[])).push(p);
 });
 var years=Object.keys(groups).sort(function(a,b){return b-a;});
 var currentYear=new Intl.DateTimeFormat('en',{year:'numeric',timeZone:'Asia/Shanghai'}).format(new Date());
 roots.forEach(function(root,mode){var fragment=document.createDocumentFragment();
  var displayYears=mode===0?years.filter(function(year){return year===currentYear;}):years;
  displayYears.forEach(function(year,index){var details=el('details');details.open=mode===0?index===0:index<2;var summary=el('summary','',year);summary.appendChild(el('span','year-count',groups[year].length+' '+(groups[year].length===1?'publication':'publications')));details.appendChild(summary);var list=el('ul','scholar-list');
   groups[year].sort(function(a,b){return a.title.localeCompare(b.title);}).forEach(function(p){var li=el('li');var link=el('a','',p.title);link.href=p.url;
    if(mode===0){var template=nextNewsTemplate();var line=el('p','news-line');line.appendChild(document.createTextNode(template[0]+'“'));line.appendChild(link);line.appendChild(document.createTextNode('”'+template[1]));li.appendChild(line);li.appendChild(metadata(p));}
    else{var heading=el('h3','paper-title');heading.appendChild(link);li.appendChild(heading);li.appendChild(authorLine(p.authors));var meta=metadata(p);var read=el('a','','Read paper ↗');read.href=p.url;meta.appendChild(read);li.appendChild(meta);}
    list.appendChild(li);
   });details.appendChild(list);fragment.appendChild(details);
  });
  if(!displayYears.length)fragment.appendChild(el('p','scholar-note',mode===0?'No publication updates for '+currentYear+' yet.':'No verified publications to display yet.'));
  root.replaceChildren(fragment);
 });
 if(Number.isInteger(data.citedby)){var total=citationBadge(data.citedby);total.href='https://scholar.google.com/citations?user='+scholarId;total.title='Google Scholar citations across all works';document.getElementById('scholar-total').replaceChildren(total);}
}
var controller=new AbortController();var timer=setTimeout(function(){controller.abort();},20000);
fetch('https://raw.githubusercontent.com/YaoYao1995/yaoyao1995.github.io/google-scholar-stats/gs_data.json',{cache:'no-store',signal:controller.signal}).then(function(r){if(!r.ok)throw new Error('Data unavailable');return r.json();}).then(render).catch(function(){roots.forEach(function(root){var p=el('p','scholar-note','Publication data is temporarily unavailable. ');var a=el('a','','View Google Scholar ↗');a.href='https://scholar.google.com/citations?user='+scholarId;p.appendChild(a);root.replaceChildren(p);});}).finally(function(){clearTimeout(timer);});
})();
</script>
