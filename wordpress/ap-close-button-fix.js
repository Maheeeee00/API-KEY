/* Move close button + steps into sticky header so it never hides on steps 3/4 */
(function () {
  var wrap = document.getElementById('apMegaWrap');
  if (!wrap || wrap.dataset.apHeaderFixed === '1') return;

  var shell = wrap.querySelector('.ap-shell');
  var container = wrap.querySelector('.ap-container');
  var btn = wrap.querySelector('.ap-close-btn');
  var steps = wrap.querySelector('.steps');
  if (!shell || !container || !btn || !steps) return;

  var header = document.createElement('div');
  header.className = 'ap-form-header';
  container.insertBefore(header, steps);
  header.appendChild(btn);
  header.appendChild(steps);

  wrap.dataset.apHeaderFixed = '1';
})();
