(() => {
  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
  if (tg) {
    try {
      tg.ready();
      tg.expand();
      tg.setHeaderColor("#121826");
      tg.setBackgroundColor("#121826");
    } catch (_) {}
  }

  const state = {
    cat: "all",
    q: "",
    selected: null,
    step: 0,
    form: { brand: "", welcome: "", admin: "", detail: "" },
  };

  const $ = (id) => document.getElementById(id);

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function toast(msg) {
    if (window.BF_UI && BF_UI.toast) BF_UI.toast(msg);
    else try { if (tg && tg.showAlert) tg.showAlert(String(msg)); else alert(msg); } catch (_) { alert(msg); }
  }

  function isValidAdminId(v) {
    return /^\d{5,15}$/.test(String(v || "").trim());
  }

  function go(name) {
    if (window.BF_UI && BF_UI.setTab) BF_UI.setTab(name);
    else {
      document.querySelectorAll(".bf-panel").forEach((p) => {
        p.classList.toggle("active", p.id === "panel-" + name);
      });
      document.querySelectorAll(".bf-tab").forEach((t) => {
        t.classList.toggle("active", t.dataset.tab === name);
      });
    }
    document.querySelectorAll(".bf-dock button").forEach((b) => {
      b.classList.toggle("active", b.dataset.go === name);
    });
    if (name === "builder") renderBuilder();
    if (name === "catalog") renderCards();
  }

  function filtered() {
    const q = state.q.trim().toLowerCase();
    const list = (window.BF_DATA && BF_DATA.templates) || [];
    return list.filter((t) => {
      const okCat = state.cat === "all" || t.cat === state.cat;
      const hay = `${t.title} ${t.blurb} ${t.key} ${t.engine}`.toLowerCase();
      return okCat && (!q || hay.includes(q));
    });
  }

  function selectedMeta() {
    const list = (window.BF_DATA && BF_DATA.templates) || [];
    return list.find((t) => t.key === state.selected) || null;
  }

  function collect() {
    const map = [
      ["fBrand", "brand"],
      ["fWelcome", "welcome"],
      ["fAdmin", "admin"],
      ["fDetail", "detail"],
    ];
    for (const [id, key] of map) {
      const el = $(id);
      if (el) state.form[key] = String(el.value || "").trim();
    }
  }

  function renderFilters() {
    const el = $("filters");
    if (!el || !BF_DATA.categories) return;
    el.innerHTML = BF_DATA.categories
      .map(
        (c) =>
          `<button type="button" class="bf-filter ${state.cat === c.id ? "active" : ""}" data-cat="${esc(c.id)}">${esc(c.title)}</button>`
      )
      .join("");
  }

  function renderCards() {
    const cards = $("cards");
    const countLabel = $("countLabel");
    if (!cards) return;
    const list = filtered();
    if (countLabel) countLabel.textContent = list.length + " قالب";
    if (!list.length) {
      cards.innerHTML = '<div class="bf-empty">چیزی پیدا نشد</div>';
      return;
    }
    const slice = list.slice(0, 60);
    cards.innerHTML =
      slice
        .map(
          (t) => `<article class="bf-card ${state.selected === t.key ? "bf-selected" : ""}">
        <div class="meta"><span class="bf-badge">${esc(t.engine)}</span></div>
        <h3>${esc(t.title)}</h3>
        <p>${esc(t.blurb)}</p>
        <button type="button" class="bf-btn bf-btn-primary" data-pick="${esc(t.key)}">انتخاب و ساخت</button>
      </article>`
        )
        .join("") +
      (list.length > 60 ? `<div class="bf-empty">+${list.length - 60} — جستجو را محدودتر کن</div>` : "");
  }

  function updateNavButtons() {
    const btnNext = $("btnNext");
    const btnPrev = $("btnPrev");
    if (btnPrev) btnPrev.disabled = state.step <= 0;
    if (btnNext) {
      if (state.step >= 4) {
        btnNext.textContent = "ارسال به ربات و ساخت ZIP";
        btnNext.dataset.action = "send";
      } else {
        btnNext.textContent = "ادامه";
        btnNext.dataset.action = "next";
      }
    }
    // Telegram native MainButton on last step
    try {
      if (!tg || !tg.MainButton) return;
      if (state.step >= 4) {
        tg.MainButton.setText("ارسال به ربات و ساخت ZIP");
        tg.MainButton.show();
        tg.MainButton.enable();
      } else {
        tg.MainButton.hide();
      }
    } catch (_) {}
  }

  function renderBuilder() {
    const body = $("builderBody");
    const pill = $("stepPill");
    const stepsEl = $("steps");
    if (pill) pill.textContent = `مرحله ${state.step + 1} از ۵`;
    if (stepsEl) {
      stepsEl.innerHTML = [0, 1, 2, 3, 4]
        .map((i) => `<div class="bf-step ${i <= state.step ? "on" : ""}"></div>`)
        .join("");
    }
    if (!body) return;
    const meta = selectedMeta();
    const s = state.step;

    if (s === 0) {
      body.innerHTML = meta
        ? `<div class="bf-panel-inner"><h3>${esc(meta.title)}</h3>
           <p class="bf-muted">${esc(meta.blurb)}</p>
           <p class="bf-muted">کلید قالب: <code>${esc(meta.key)}</code></p>
           <p>روی <b>ادامه</b> بزن و برند را وارد کن.</p></div>`
        : `<div class="bf-panel-inner"><p>هنوز قالبی انتخاب نشده.</p>
           <button type="button" class="bf-btn bf-btn-primary" data-go="catalog">انتخاب قالب</button></div>`;
    } else if (s === 1) {
      body.innerHTML = `<label class="bf-label">نام برند *</label>
        <input class="bf-input" id="fBrand" maxlength="40" value="${esc(state.form.brand)}" placeholder="مثلاً VIP Shop" />
        <label class="bf-label">پیام خوش‌آمد</label>
        <textarea class="bf-input" id="fWelcome" rows="3" placeholder="به فروشگاه ما خوش آمدید">${esc(state.form.welcome)}</textarea>`;
    } else if (s === 2) {
      body.innerHTML = `<label class="bf-label">جزئیات قالب (اختیاری)</label>
        <textarea class="bf-input" id="fDetail" rows="5" placeholder="منو، قیمت، زمان‌ها یا خط تیره -">${esc(state.form.detail)}</textarea>`;
    } else if (s === 3) {
      body.innerHTML = `<label class="bf-label">آیدی عددی ادمین *</label>
        <input class="bf-input" id="fAdmin" inputmode="numeric" value="${esc(state.form.admin)}" placeholder="مثلاً 7767354117" />
        <p class="bf-muted">فقط عدد — از @userinfobot</p>`;
    } else {
      body.innerHTML = `<div class="bf-panel-inner">
        <h3>تأیید و ارسال</h3>
        <p>قالب: <b>${esc(meta ? meta.title : state.selected || "—")}</b></p>
        <p>برند: <b>${esc(state.form.brand || "—")}</b></p>
        <p>ادمین: <b>${esc(state.form.admin || "—")}</b></p>
        <p class="bf-muted">با زدن دکمه پایین، داده به ربات کارخانه می‌رود و <b>فایل ZIP</b> در چت ربات می‌آید.</p>
        <button type="button" class="bf-btn bf-btn-primary" id="btnSendBot">ارسال به ربات و ساخت ZIP</button>
      </div>`;
    }
    updateNavButtons();
  }

  function validateStep() {
    collect();
    if (state.step === 0 && !state.selected) {
      toast("اول یک قالب انتخاب کن");
      return false;
    }
    if (state.step === 1 && !state.form.brand) {
      toast("نام برند لازم است");
      return false;
    }
    if (state.step === 3 && !isValidAdminId(state.form.admin)) {
      toast("آیدی ادمین باید فقط عدد ۵ تا ۱۵ رقمی باشد");
      return false;
    }
    return true;
  }

  function validateAll() {
    collect();
    if (!state.selected) {
      toast("قالب انتخاب نشده");
      return false;
    }
    if (!state.form.brand) {
      toast("نام برند لازم است");
      return false;
    }
    if (!isValidAdminId(state.form.admin)) {
      toast("آیدی ادمین نامعتبر است");
      return false;
    }
    return true;
  }

  function sendToBot() {
    if (!validateAll()) return;

    const payload = {
      template: state.selected,
      brand: state.form.brand,
      welcome: state.form.welcome || `به ${state.form.brand} خوش آمدید`,
      admin: state.form.admin,
      detail: state.form.detail || "",
    };
    const raw = JSON.stringify(payload);
    if (raw.length > 4096) {
      toast("داده خیلی بزرگ است");
      return;
    }

    // Must be opened inside Telegram from bot WebApp button
    const hasInit = !!(tg && tg.initData && String(tg.initData).length > 0);
    if (!tg) {
      toast("این صفحه را داخل تلگرام و از دکمه ربات باز کن");
      return;
    }
    if (!hasInit) {
      toast("مینی‌اپ را از دکمه داخل ربات کارخانه باز کن (نه لینک مرورگر)");
      return;
    }
    if (typeof tg.sendData !== "function") {
      toast("این نسخه تلگرام sendData ندارد — تلگرام را آپدیت کن");
      return;
    }

    try {
      tg.sendData(raw);
      toast("ارسال شد — به چت ربات برگرد؛ ZIP می‌آید");
      try {
        if (tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");
      } catch (_) {}
      // Mini App usually closes; if not, user can close
      setTimeout(() => {
        try {
          tg.close();
        } catch (_) {}
      }, 400);
    } catch (e) {
      console.error(e);
      toast("ارسال ناموفق بود. از دکمه WebApp داخل ربات دوباره باز کن");
    }
  }

  function onNext() {
    const btn = $("btnNext");
    const action = (btn && btn.dataset.action) || (state.step >= 4 ? "send" : "next");
    if (action === "send" || state.step >= 4) {
      sendToBot();
      return;
    }
    if (!validateStep()) return;
    state.step = Math.min(4, state.step + 1);
    renderBuilder();
  }

  function onPrev() {
    collect();
    state.step = Math.max(0, state.step - 1);
    renderBuilder();
  }

  // Events
  document.body.addEventListener("click", (e) => {
    const t = e.target.closest("[data-go]");
    if (t && t.dataset.go) {
      go(t.dataset.go);
      return;
    }
    const cat = e.target.closest("[data-cat]");
    if (cat) {
      state.cat = cat.dataset.cat;
      renderFilters();
      renderCards();
      return;
    }
    const pick = e.target.closest("[data-pick]");
    if (pick) {
      state.selected = pick.dataset.pick;
      state.step = 0;
      renderCards();
      go("builder");
      toast("قالب انتخاب شد — ادامه را بزن");
      return;
    }
    if (e.target.id === "btnSendBot" || e.target.closest("#btnSendBot")) {
      e.preventDefault();
      sendToBot();
    }
  });

  const search = $("search");
  if (search) {
    let tmr;
    search.addEventListener("input", () => {
      clearTimeout(tmr);
      tmr = setTimeout(() => {
        state.q = search.value || "";
        renderCards();
      }, 100);
    });
  }

  const btnPrev = $("btnPrev");
  const btnNext = $("btnNext");
  if (btnPrev) btnPrev.addEventListener("click", (e) => { e.preventDefault(); onPrev(); });
  if (btnNext) btnNext.addEventListener("click", (e) => { e.preventDefault(); onNext(); });

  try {
    if (tg && tg.MainButton) {
      tg.MainButton.onClick(() => sendToBot());
    }
    if (tg && tg.BackButton) {
      tg.BackButton.onClick(() => go("catalog"));
    }
  } catch (_) {}

  if (!window.BF_DATA) {
    toast("خطا در بارگذاری قالب‌ها");
    return;
  }
  renderFilters();
  renderCards();
  // default tab
  go("catalog");
  renderBuilder();

  const faq = $("faq");
  if (faq && BF_DATA.faq) {
    faq.innerHTML = BF_DATA.faq
      .map((f) => `<details class="bf-faq"><summary>${esc(f.q)}</summary><p>${esc(f.a)}</p></details>`)
      .join("");
  }
  const gallery = $("gallery");
  if (gallery && BF_DATA.gallery) {
    gallery.innerHTML = BF_DATA.gallery.map((g) => `<div class="bf-g-item">${esc(g)}</div>`).join("");
  }
})();
