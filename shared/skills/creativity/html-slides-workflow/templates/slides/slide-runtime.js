(() => {
  function fit() {
    const slide = document.querySelector('.slide');
    if (!slide) return;
    const { width, height } = getComputedStyle(slide);
    const scale = Math.min(innerWidth / parseFloat(width), innerHeight / parseFloat(height));
    document.documentElement.style.setProperty('--slide-scale', String(scale));
  }
  addEventListener('resize', fit);
  document.fonts.ready.then(fit);
  fit();
})();
