
window.BF_UI = {
  toast(msg) {
    const old = document.querySelector('.bf-toast');
    if (old) old.remove();
    const el = document.createElement('div');
    el.className = 'bf-toast';
    el.textContent = String(msg ?? '');
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 2300);
  },
  setTab(name) {
    const n = String(name || '');
    document.querySelectorAll('.bf-tab').forEach((t) => {
      t.classList.toggle('active', t.dataset.tab === n);
    });
    document.querySelectorAll('.bf-panel').forEach((p) => {
      p.classList.toggle('active', p.id === 'panel-' + n);
    });
  },
  haptic(type) {
    try {
      const h = window.Telegram?.WebApp?.HapticFeedback;
      if (!h?.impactOccurred) return;
      const allowed = ['light', 'medium', 'heavy', 'rigid', 'soft'];
      h.impactOccurred(allowed.includes(type) ? type : 'light');
    } catch (_) {}
  }
};
