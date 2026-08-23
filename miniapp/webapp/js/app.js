(() => {
  const tg = window.Telegram?.WebApp;
  if (tg) {
    try {
      tg.ready();
      tg.expand();
      tg.setHeaderColor('#06060e');
      tg.setBackgroundColor('#06060e');
    } catch (_) {}
  }

  const state = {
    cat: 'all',
    q: '',
    selected: null,
    step: 0,
    form: { brand: '', welcome: '', admin: '', detail: '' }
  };

  const $ = (id) => document.getElementById(id);

  function esc(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function filtered() {
    const q = state.q.trim().toLowerCase();
    const data = window.BF_DATA;
    if (!data?.templates) return [];
    return data.templates.filter((t) => {
      const okCat = state.cat === 'all' || t.cat === state.cat;
      const hay = `${t.title} ${t.blurb} ${t.key} ${t.engine}`.toLowerCase();
      const okQ = !q || hay.includes(q);
      return okCat && okQ;
    });
  }

  function renderFilters() {
    const filters = $('filters');
    if (!filters || !window.BF_DATA?.categories) return;
    filters.innerHTML = BF_DATA.categories
      .map(
        (c) =>
          `<button type="button" class="bf-filter bf-focus-ring ${
            state.cat === c.id ? 'active' : ''
          }" data-cat="${esc(c.id)}">${esc(c.title)}</button>`
      )
      .join('');
  }

  function renderCards() {
    const cards = $('cards');
    const countLabel = $('countLabel');
    if (!cards) return;
    const list = filtered();
    if (countLabel) countLabel.textContent = list.length + ' مورد';
    if (!list.length) {
      cards.innerHTML = '<div class="bf-empty glass">چیزی پیدا نشد</div>';
      return;
    }
    cards.innerHTML = list
      .map(
        (t) => `
      <article class="bf-card ${state.selected === t.key ? 'bf-selected' : ''}">
        <div class="meta"><span class="bf-badge">${esc(t.engine)}</span><span>${esc(t.cat)}</span></div>
        <h3>${esc(t.title)}</h3>
        <p>${esc(t.blurb)}</p>
        <button type="button" class="bf-btn bf-btn-primary bf-focus-ring" data-pick="${esc(t.key)}">انتخاب</button>
      </article>`
      )
      .join('');
  }

  function renderGallery() {
    const el = $('gallery');
    if (!el || !BF_DATA?.gallery) return;
    el.innerHTML = BF_DATA.gallery
      .map((g) => `<div class="bf-g-item">${esc(g)}</div>`)
      .join('');
  }

  function renderFaq() {
    const el = $('faq');
    if (!el || !BF_DATA?.faq) return;
    el.innerHTML = BF_DATA.faq
      .map(
        (f) =>
          `<details><summary>${esc(f.q)}</summary><p>${esc(f.a)}</p></details>`
      )
      .join('');
  }

  function renderSteps() {
    const stepsEl = $('steps');
    const pill = $('stepPill');
    if (stepsEl) {
      stepsEl.innerHTML = [0, 1, 2, 3, 4]
        .map((i) => `<div class="bf-step ${i <= state.step ? 'on' : ''}"></div>`)
        .join('');
    }
    if (pill) pill.textContent = `مرحله ${state.step + 1} از 5`;
  }

  function updatePreview() {
    const n = $('pvName');
    const w = $('pvWelcome');
    if (n) n.textContent = state.form.brand || 'نام برند';
    if (w) w.textContent = state.form.welcome || 'پیام خوش‌آمد اینجا دیده می‌شود';
  }

  function renderBuilder() {
    const builderBody = $('builderBody');
    if (!builderBody) return;
    renderSteps();
    updatePreview();
    const s = state.step;
    if (s === 0) {
      const title = state.selected
        ? BF_DATA.templates.find((x) => x.key === state.selected)?.title ||
          state.selected
        : 'هنوز انتخاب نشده';
      builderBody.innerHTML = `
        <div class="bf-field"><label>قالب</label>
        <input value="${esc(title)}" readonly /></div>
        <p class="bf-muted">از تب قالب‌ها یکی را انتخاب کن.</p>`;
    } else if (s === 1) {
      builderBody.innerHTML = `<div class="bf-field"><label>نام برند</label>
        <input id="fBrand" class="bf-focus-ring" value="${esc(
          state.form.brand
        )}" placeholder="مثلاً Nova Shop" maxlength="64" /></div>`;
    } else if (s === 2) {
      builderBody.innerHTML = `<div class="bf-field"><label>پیام خوش‌آمد</label>
        <textarea id="fWelcome" class="bf-focus-ring" placeholder="متن شیک خوش‌آمد..." maxlength="500">${esc(
          state.form.welcome
        )}</textarea></div>`;
    } else if (s === 3) {
      builderBody.innerHTML = `<div class="bf-field"><label>آیدی عددی ادمین</label>
        <input id="fAdmin" class="bf-focus-ring" value="${esc(
          state.form.admin
        )}" inputmode="numeric" placeholder="7767..." maxlength="20" /></div>`;
    } else {
      builderBody.innerHTML = `
        <div class="bf-field"><label>جزئیات قالب</label>
        <textarea id="fDetail" class="bf-focus-ring" placeholder="عنوان | قیمت | توضیح" maxlength="4000">${esc(
          state.form.detail
        )}</textarea></div>
        <p class="bf-muted">ZIP نهایی را از ربات کارخانه دریافت کن. اینجا آماده‌سازی برند است.</p>
        <button class="bf-btn bf-btn-primary bf-focus-ring" id="btnSendBot" type="button">ارسال خلاصه به ربات</button>`;
    }
    bindPreviewInputs();
  }

  function bindPreviewInputs() {
    const b = $('fBrand');
    const w = $('fWelcome');
    if (b) {
      b.addEventListener('input', () => {
        state.form.brand = b.value;
        updatePreview();
      });
    }
    if (w) {
      w.addEventListener('input', () => {
        state.form.welcome = w.value;
        updatePreview();
      });
    }
  }

  function collect() {
    const b = $('fBrand');
    const w = $('fWelcome');
    const a = $('fAdmin');
    const d = $('fDetail');
    if (b) state.form.brand = b.value.trim();
    if (w) state.form.welcome = w.value.trim();
    if (a) state.form.admin = a.value.trim();
    if (d) state.form.detail = d.value.trim();
    updatePreview();
  }

  function isValidAdminId(v) {
    return /^\d{5,20}$/.test(String(v || '').trim());
  }

  function go(tab) {
    if (!tab) return;
    BF_UI.setTab(tab);
    BF_UI.haptic('light');
  }

  function applyTheme(dawn) {
    if (dawn) document.documentElement.setAttribute('data-theme', 'dawn');
    else document.documentElement.removeAttribute('data-theme');
    const color = dawn ? '#f7f4ff' : '#06060e';
    const meta = $('metaTheme');
    if (meta) meta.setAttribute('content', color);
    try {
      tg?.setHeaderColor?.(color);
      tg?.setBackgroundColor?.(color);
    } catch (_) {}
  }

  // Events
  const tabs = $('tabs');
  if (tabs) {
    tabs.addEventListener('click', (e) => {
      const t = e.target.closest('[data-tab]');
      if (t) go(t.dataset.tab);
    });
  }

  document.querySelectorAll('[data-go]').forEach((el) => {
    el.addEventListener('click', () => go(el.dataset.go));
  });

  const q = $('q');
  if (q) {
    q.addEventListener('input', (e) => {
      state.q = e.target.value;
      renderCards();
    });
  }

  const filters = $('filters');
  if (filters) {
    filters.addEventListener('click', (e) => {
      const b = e.target.closest('[data-cat]');
      if (!b) return;
      state.cat = b.dataset.cat;
      renderFilters();
      renderCards();
      BF_UI.haptic('light');
    });
  }

  const cards = $('cards');
  if (cards) {
    cards.addEventListener('click', (e) => {
      const pick = e.target.closest('[data-pick]');
      if (!pick) return;
      state.selected = pick.dataset.pick;
      renderCards();
      state.step = 0;
      go('builder');
      renderBuilder();
      BF_UI.toast('قالب انتخاب شد');
    });
  }

  const btnPrev = $('btnPrev');
  const btnNext = $('btnNext');
  if (btnPrev) {
    btnPrev.addEventListener('click', () => {
      collect();
      state.step = Math.max(0, state.step - 1);
      renderBuilder();
    });
  }
  if (btnNext) {
    btnNext.addEventListener('click', () => {
      collect();
      if (state.step === 0 && !state.selected)
        return BF_UI.toast('اول قالب را انتخاب کن');
      if (state.step === 1 && !state.form.brand)
        return BF_UI.toast('نام برند لازم است');
      if (state.step === 3 && !isValidAdminId(state.form.admin))
        return BF_UI.toast('آیدی ادمین باید فقط عدد باشد');
      state.step = Math.min(4, state.step + 1);
      renderBuilder();
    });
  }

  const builderBody = $('builderBody');
  if (builderBody) {
    builderBody.addEventListener('click', (e) => {
      if (e.target.id !== 'btnSendBot') return;
      collect();
      if (!state.selected) return BF_UI.toast('قالب انتخاب نشده');
      if (!state.form.brand) return BF_UI.toast('نام برند لازم است');
      if (!isValidAdminId(state.form.admin))
        return BF_UI.toast('آیدی ادمین نامعتبر است');
      const payload = {
        template: state.selected,
        brand: state.form.brand,
        welcome: state.form.welcome,
        admin: state.form.admin,
        detail: state.form.detail
      };
      try {
        if (tg?.sendData) {
          tg.sendData(JSON.stringify(payload));
          BF_UI.toast('ارسال شد');
          return;
        }
      } catch (_) {}
      BF_UI.toast('ساخت را در ربات ادامه بده');
      console.log(payload);
    });
  }

  const btnTheme = $('btnTheme');
  if (btnTheme) {
    btnTheme.addEventListener('click', () => {
      const dawn = document.documentElement.getAttribute('data-theme') !== 'dawn';
      applyTheme(dawn);
      BF_UI.haptic('medium');
    });
  }

  const btnBrand = $('btnBrand');
  if (btnBrand) btnBrand.addEventListener('click', () => go('showcase'));

  // Boot
  if (!window.BF_DATA) {
    BF_UI.toast('خطا در بارگذاری داده');
    return;
  }
  renderFilters();
  renderCards();
  renderBuilder();
  renderGallery();
  renderFaq();
})();
