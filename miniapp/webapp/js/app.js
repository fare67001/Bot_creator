(() => {
  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
  if (tg) {
    try {
      tg.ready();
      tg.expand();
      tg.setHeaderColor("#121826");
      tg.setBackgroundColor("#121826");
      if (tg.disableVerticalSwipes) tg.disableVerticalSwipes();
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

  function haptic(kind) {
    try {
      if (!tg || !tg.HapticFeedback) return;
      if (kind === "ok") tg.HapticFeedback.notificationOccurred("success");
      else if (kind === "err") tg.HapticFeedback.notificationOccurred("error");
      else tg.HapticFeedback.impactOccurred("light");
    } catch (_) {}
  }

  function toast(msg, kind) {
    if (window.BF_UI && BF_UI.toast) BF_UI.toast(msg);
    else alert(msg);
    haptic(kind === "err" ? "err" : "ok");
  }

  function isValidAdminId(v) {
    return /^\d{5,15}$/.test(String(v || "").trim());
  }

  function filtered() {
    const q = state.q.trim().toLowerCase();
    const data = window.BF_DATA;
    if (!data || !data.templates) return [];
    return data.templates.filter((t) => {
      const okCat = state.cat === "all" || t.cat === state.cat;
      const hay = `${t.title} ${t.blurb} ${t.key} ${t.engine}`.toLowerCase();
      return okCat && (!q || hay.includes(q));
    });
  }

  function selectedMeta() {
    return (window.BF_DATA && BF_DATA.templates || []).find((t) => t.key === state.selected) || null;
  }

  function collect() {
    const brand = $("fBrand");
    const welcome = $("fWelcome");
    const admin = $("fAdmin");
    const detail = $("fDetail");
    if (brand) state.form.brand = brand.value.trim();
    if (welcome) state.form.welcome = welcome.value.trim();
    if (admin) state.form.admin = admin.value.trim();
    if (detail) state.form.detail = detail.value.trim();
  }

  function go(view) {
    document.querySelectorAll(".bf-view").forEach((el) => {
      el.classList.toggle("active", el.dataset.view === view);
    });
    document.querySelectorAll(".bf-dock button").forEach((b) => {
      b.classList.toggle("active", b.dataset.go === view);
    });
    try {
      if (tg && tg.BackButton) {
        if (view === "builder" || view === "showcase" || view === "faq") tg.BackButton.show();
        else tg.BackButton.hide();
      }
    } catch (_) {}
  }

  function renderFilters() {
    const filters = $("filters");
    if (!filters || !BF_DATA.categories) return;
    filters.innerHTML = BF_DATA.categories
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
    // virtual-ish: max 60 visible for performance; search narrows
    const slice = list.slice(0, 60);
    cards.innerHTML =
      slice
        .map(
          (t) => `<article class="bf-card ${state.selected === t.key ? "bf-selected" : ""}">
        <div class="meta"><span class="bf-badge">${esc(t.engine)}</span></div>
        <h3>${esc(t.title)}</h3>
        <p>${esc(t.blurb)}</p>
        <button type="button" class="bf-btn bf-btn-primary" data-pick="${esc(t.key)}">انتخاب</button>
      </article>`
        )
        .join("") +
      (list.length > 60
        ? `<div class="bf-empty">+${list.length - 60} مورد دیگر — جستجو را محدودتر کن</div>`
        : "");
  }

  function renderSteps() {
    const stepsEl = $("steps");
    const pill = $("stepPill");
    if (stepsEl) {
      stepsEl.innerHTML = [0, 1, 2, 3, 4]
        .map((i) => `<div class="bf-step ${i <= state.step ? "on" : ""}"></div>`)
        .join("");
    }
    if (pill) pill.textContent = `مرحله ${state.step + 1} از ۵`;
    const btnNext = $("btnNext");
    if (btnNext) {
      if (state.step >= 4) {
        btnNext.textContent = "ساخت و ارسال به ربات";
        btnNext.dataset.mode = "send";
      } else {
        btnNext.textContent = "ادامه";
        btnNext.dataset.mode = "next";
      }
    }
  }

  function renderBuilder() {
    const body = $("builderBody");
    if (!body) return;
    renderSteps();
    const meta = selectedMeta();
    const s = state.step;
    if (s === 0) {
      body.innerHTML = meta
        ? `<div class="bf-panel"><h3>${esc(meta.title)}</h3><p class="bf-muted">${esc(meta.blurb)}</p>
           <p class="bf-muted">کلید: <code>${esc(meta.key)}</code></p></div>`
        : `<div class="bf-panel"><p>اول از «خانه / قالب‌ها» یک قالب انتخاب کن.</p>
           <button type="button" class="bf-btn bf-btn-primary" data-go="catalog">رفتن به قالب‌ها</button></div>`;
    } else if (s === 1) {
      body.innerHTML = `<label class="bf-label">نام برند</label>
        <input class="bf-input" id="fBrand" maxlength="40" value="${esc(state.form.brand)}" placeholder="مثلاً VIP Shop" />
        <label class="bf-label">پیام خوش‌آمد (اختیاری)</label>
        <textarea class="bf-input" id="fWelcome" rows="3" placeholder="به فروشگاه ما خوش آمدید">${esc(state.form.welcome)}</textarea>`;
    } else if (s === 2) {
      body.innerHTML = `<label class="bf-label">جزئیات قالب (اختیاری)</label>
        <textarea class="bf-input" id="fDetail" rows="5" placeholder="منو، قیمت‌ها، زمان‌ها یا -">${esc(state.form.detail)}</textarea>`;
    } else if (s === 3) {
      body.innerHTML = `<label class="bf-label">آیدی عددی ادمین</label>
        <input class="bf-input" id="fAdmin" inputmode="numeric" value="${esc(state.form.admin)}" placeholder="مثلاً 7767354117" />
        <p class="bf-muted">فقط عدد — از @userinfobot بگیر</p>`;
    } else {
      body.innerHTML = `<div class="bf-panel">
        <h3>خلاصه نهایی</h3>
        <p>قالب: <b>${esc(meta ? meta.title : state.selected || "—")}</b></p>
        <p>برند: <b>${esc(state.form.brand || "—")}</b></p>
        <p>ادمین: <b>${esc(state.form.admin || "—")}</b></p>
        <p class="bf-muted">با زدن دکمه پایین، خلاصه به ربات ارسال می‌شود و ZIP در چت می‌آید.</p>
        <button class="bf-btn bf-btn-primary" id="btnSendBot" type="button">ساخت و ارسال به ربات</button>
      </div>`;
    }
  }

  function buildPayload() {
    collect();
    return {
      template: state.selected,
      brand: state.form.brand,
      welcome: state.form.welcome,
      admin: state.form.admin,
      detail: state.form.detail,
    };
  }

  function validateForSend() {
    collect();
    if (!state.selected) {
      toast("اول قالب را انتخاب کن", "err");
      return false;
    }
    if (!state.form.brand) {
      toast("نام برند لازم است", "err");
      return false;
    }
    if (!isValidAdminId(state.form.admin)) {
      toast("آیدی ادمین باید فقط عدد باشد", "err");
      return false;
    }
    return true;
  }

  function sendToBot() {
    if (!validateForSend()) return;
    const payload = buildPayload();
    const raw = JSON.stringify(payload);
    if (raw.length > 4096) {
      toast("داده خیلی بزرگ است", "err");
      return;
    }
    try {
      if (tg && typeof tg.sendData === "function") {
        tg.sendData(raw);
        toast("ارسال شد — ربات ZIP را می‌فرستد");
        // Mini App closes after sendData; if not, show hint
        setTimeout(() => {
          toast("اگر ZIP نیامد، از داخل ربات دوباره مینی‌اپ را باز کن");
        }, 1500);
        return;
      }
    } catch (e) {
      console.error(e);
    }
    toast("مینی‌اپ را فقط از دکمه داخل ربات باز کن، بعد دوباره بفرست", "err");
    console.log("payload", payload);
  }

  function nextStep() {
    collect();
    const btnNext = $("btnNext");
    if (btnNext && btnNext.dataset.mode === "send") {
      sendToBot();
      return;
    }
    if (state.step === 0 && !state.selected) return toast("اول قالب را انتخاب کن", "err");
    if (state.step === 1 && !state.form.brand) return toast("نام برند لازم است", "err");
    if (state.step === 3 && !isValidAdminId(state.form.admin))
      return toast("آیدی ادمین باید فقط عدد باشد", "err");
    state.step = Math.min(4, state.step + 1);
    renderBuilder();
    haptic();
  }

  // events
  document.body.addEventListener("click", (e) => {
    const goBtn = e.target.closest("[data-go]");
    if (goBtn) {
      go(goBtn.dataset.go);
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
      renderBuilder();
      toast("قالب انتخاب شد");
      return;
    }
    if (e.target.id === "btnSendBot") {
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
      }, 120);
    });
  }

  const btnPrev = $("btnPrev");
  const btnNext = $("btnNext");
  if (btnPrev)
    btnPrev.addEventListener("click", () => {
      collect();
      state.step = Math.max(0, state.step - 1);
      renderBuilder();
    });
  if (btnNext) btnNext.addEventListener("click", nextStep);

  try {
    if (tg && tg.BackButton) {
      tg.BackButton.onClick(() => go("catalog"));
    }
  } catch (_) {}

  if (!window.BF_DATA) {
    toast("خطا در بارگذاری داده", "err");
    return;
  }
  renderFilters();
  renderCards();
  renderBuilder();
  // light faq/gallery
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
  const metric = document.querySelector(".bf-hero-metrics b");
  if (metric) metric.textContent = String((BF_DATA.templates || []).length);
})();
