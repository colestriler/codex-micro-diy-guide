(() => {
  const params = new URLSearchParams(location.search);
  const view = document.getElementById('mc-view');
  const trace = document.getElementById('mc-trace');
  if (params.has('trace') || params.get('view') === 'board') {
    view.value = 'board'; view.dispatchEvent(new Event('change'));
  }
  if ([...trace.options].some(option => option.value === params.get('trace'))) {
    trace.value = params.get('trace'); trace.dispatchEvent(new Event('change'));
  }
  let lastHeight = 0;
  const report = () => {
    const height = Math.ceil(document.body.getBoundingClientRect().height);
    if (height !== lastHeight && window.parent !== window) {
      lastHeight = height;
      window.parent.postMessage({type:'micro:wiring-height',height},location.origin);
    }
  };
  new ResizeObserver(report).observe(document.body);
  report();
})();
