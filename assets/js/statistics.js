(() => {
  const statistics = document.querySelector('[data-site-statistics]');
  if (!statistics) return;

  const loading = statistics.querySelector('[data-statistics-loading]');
  const unavailable = statistics.querySelector('[data-statistics-unavailable]');
  const counters = ['site_pv', 'site_uv'].map((name) => document.getElementById(`busuanzi_value_${name}`));

  if (!['xiuyue.org', 'www.xiuyue.org'].includes(window.location.hostname)) {
    loading.hidden = true;
    unavailable.hidden = true;
    return;
  }
  loading.hidden = false;

  const hasCounts = () => counters.every((counter) => /^\d+$/.test(counter.textContent.trim()));
  const updateStatus = () => {
    if (!hasCounts()) return;
    loading.hidden = true;
    unavailable.hidden = true;
    window.clearTimeout(deadline);
    observer.disconnect();
  };
  const showUnavailable = () => {
    if (hasCounts()) {
      updateStatus();
      return;
    }
    loading.hidden = true;
    unavailable.hidden = false;
  };

  const observer = new MutationObserver(updateStatus);
  counters.forEach((counter) => observer.observe(counter, { childList: true, characterData: true, subtree: true }));
  const deadline = window.setTimeout(showUnavailable, 10000);

  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js';
  script.onerror = showUnavailable;
  document.head.appendChild(script);
})();
