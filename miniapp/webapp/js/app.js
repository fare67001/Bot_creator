/* BF_VERSION v7-FIXED */
(() => {
  "use strict";

  const tg =
    window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
  if (tg) {
    try {
      tg.ready();
      tg.expand();
      if (tg.setHeaderColor) tg.setHeaderColor("#121826");
      if (tg.setBackgroundColor) tg.setBackgroundColor("#121826");
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
    else {
      try {
        if (tg && tg.showAlert) tg.showAlert(String(msg));
        else alert(String(msg));
      } catch (_) {
        try {
          alert(String(msg));
        } catch (__) {}
      }
    }
  }

  function haptic(type) {
    if (window.BF_UI && BF_UI.haptic) BF_UI.haptic(type);
  }

  function isValidAdminId(v) {
    return /^\d{5,15}$/.test(String(v || "").trim());
  }

  function go(name) {
    name = String(name || "catalog");
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
    haptic("light");
  }

  function filtered() {
    const q = state.q.trim().toLowerCase();
    const list = (window.BF_DATA && BF_DATA.templates) || [];
    return list.filter((t) => {
      const okCat = state.cat === "all" || t.cat === state.cat;
      const hay = `${t.title || ""} ${t.blurb || ""} ${t.key || ""} ${t.engine || ""}`.toLowerCase();
      return okCat && (!q || hay.includes(q));
    });
  }

  function selectedMeta() {
    const list = (window.BF_DATA && BF_DATA.templates) || [];
    return list.find((t) => t.key === state.selected) || null;
  }

  function collect() {
    const brand = $("fBrand");
    const welcome = $("fWelcome");
    const admin = $("fAdmin");
    const detail = $("fDetail");
    if (brand) state.form.brand = String(brand.value || "").trim();
    if (welcome) state.form.welcome = String(welcome.value || "").trim();
    if (admin) state.form.admin = String(admin.value || "").trim();
    if (detail) state.form.detail = String(detail.value || "").trim();
  }

  function renderFilters() {
    const el = $("filters");
    if (!el) return;
    const cats = (window.BF_DATA && BF_DATA.categories) || [
      { id: "all", title: "همه" },
    ];
    el.innerHTML = cats
      .map(
        (c) =>
          `<button type="button" class="bf-filter ${
            state.cat === c.id ? "active" : ""
          }" data-cat="${esc(c.id)}">${esc(c.title)}</button>`
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
      cards.innerHTML =
        '<div class="bf-empty">چیزی پیدا نشد. دسته یا جستجو را عوض کن.</div>';
      return;
    }
    const PAGE = 48;
    const slice = list.slice(0, PAGE);
    cards.innerHTML =
      slice
        .map((t) => {
          return `<article class="bf-card ${
            state.selected === t.key ? "bf-selected" : ""
          }">
        <div class="meta">
          <span class="bf-badge">${esc(t.engine || "bot")}</span>
        </div>
        <h3>${esc(t.title)}</h3>
        <p>${esc(t.blurb || "")}</p>
        <button type="button" class="bf-btn bf-btn-primary" data-pick="${esc(
          t.key
        )}">انتخاب و ساخت</button>
      </article>`;
        })
        .join("") +
      (list.length > PAGE
        ? `<div class="bf-empty">نمایش ${PAGE} از ${list.length} — برای بقیه جستجو کن</div>`
        : "");
  }

  function updateNavButtons() {
    const btnNext = $("btnNext");
    const btnPrev = $("btnPrev");
    if (btnPrev) btnPrev.disabled = state.step <= 0;
    if (btnNext) {
      if (state.step >= 4) {
        btnNext.textContent = "ارسال و دانلود ZIP";
        btnNext.dataset.action = "send";
      } else {
        btnNext.textContent = "ادامه";
        btnNext.dataset.action = "next";
      }
      btnNext.disabled = false;
    }
    try {
      if (!tg || !tg.MainButton) return;
      if (state.step >= 4) {
        tg.MainButton.setText("ارسال و دانلود ZIP");
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
        ? `<div class="bf-panel-inner">
            <h3>${esc(meta.title)}</h3>
            <p class="bf-muted">${esc(meta.blurb || "")}</p>
            <p class="bf-muted">کلید: <code>${esc(meta.key)}</code></p>
            <p>روی <b>ادامه</b> بزن و برند را وارد کن.</p>
          </div>`
        : `<div class="bf-panel-inner"><p>هنوز قالبی انتخاب نشده.</p>
           <button type="button" class="bf-btn bf-btn-primary" data-go="catalog">انتخاب قالب</button></div>`;
    } else if (s === 1) {
      body.innerHTML = `
        <label class="bf-label" for="fBrand">نام برند / فروشگاه *</label>
        <input class="bf-input" id="fBrand" maxlength="40" value="${esc(
          state.form.brand
        )}" placeholder="مثلاً VIP Shop" autocomplete="organization" />
        <label class="bf-label" for="fWelcome">پیام خوش‌آمد</label>
        <textarea class="bf-input" id="fWelcome" rows="3" placeholder="به فروشگاه ما خوش آمدید">${esc(
          state.form.welcome
        )}</textarea>`;
    } else if (s === 2) {
      body.innerHTML = `
        <label class="bf-label" for="fDetail">جزئیات قالب (اختیاری)</label>
        <textarea class="bf-input" id="fDetail" rows="5" placeholder="منو، قیمت، زمان‌ها یا -">${esc(
          state.form.detail
        )}</textarea>`;
    } else if (s === 3) {
      body.innerHTML = `
        <label class="bf-label" for="fAdmin">آیدی عددی ادمین *</label>
        <input class="bf-input" id="fAdmin" inputmode="numeric" pattern="[0-9]*" value="${esc(
          state.form.admin
        )}" placeholder="مثلاً 7767354117" autocomplete="off" />
        <p class="bf-muted">فقط عدد ۵ تا ۱۵ رقمی — از @userinfobot</p>`;
    } else {
      body.innerHTML = `<div class="bf-panel-inner">
        <h3>تأیید نهایی</h3>
        <p>قالب: <b>${esc(meta ? meta.title : state.selected || "—")}</b></p>
        <p>برند: <b>${esc(state.form.brand || "—")}</b></p>
        <p>ادمین: <b>${esc(state.form.admin || "—")}</b></p>
        <p class="bf-muted">با زدن دکمه، خلاصه به ربات ارسال می‌شود و ZIP هم قابل دانلود است.</p>
        <button type="button" class="bf-btn bf-btn-primary" id="btnSendBot">ارسال و دانلود ZIP</button>
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

  function buildPayload() {
    collect();
    return {
      template: state.selected,
      brand: state.form.brand,
      welcome: state.form.welcome || `به ${state.form.brand} خوش آمدید`,
      admin: state.form.admin,
      detail: state.form.detail || "",
    };
  }

  async function downloadZipFromApi(payload) {
    const res = await fetch("/api/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      let msg = "ساخت ZIP ناموفق";
      try {
        const j = await res.json();
        msg = j.detail || msg;
      } catch (_) {}
      throw new Error(typeof msg === "string" ? msg : "خطا");
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bot_${(payload.brand || "bot")
      .replace(/\s+/g, "_")
      .slice(0, 24)}.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  async function sendToBot() {
    if (!validateAll()) return;
    const payload = buildPayload();
    const raw = JSON.stringify(payload);
    if (raw.length > 4096) {
      toast("داده خیلی بزرگ است");
      return;
    }

    try {
      if (tg && tg.MainButton) tg.MainButton.showProgress(false);
    } catch (_) {}

    let sent = false;
    const hasInit = !!(tg && tg.initData && String(tg.initData).length > 0);
    if (tg && hasInit && typeof tg.sendData === "function") {
      try {
        tg.sendData(raw);
        sent = true;
      } catch (e) {
        console.error("sendData failed", e);
      }
    }

    try {
      await downloadZipFromApi(payload);
      toast(sent ? "ارسال به ربات + دانلود ZIP" : "ZIP دانلود شد");
    } catch (e) {
      console.error(e);
      if (sent) {
        toast("به ربات ارسال شد — به چت برگرد");
      } else {
        toast(
          "ارسال ناموفق. مینی‌اپ را از دکمه داخل پیام ربات باز کن. " +
            (e && e.message ? e.message : "")
        );
      }
    }

    try {
      if (tg && tg.MainButton) tg.MainButton.hideProgress();
    } catch (_) {}

    if (sent) {
      setTimeout(() => {
        try {
          if (tg && tg.close) tg.close();
        } catch (_) {}
      }, 1800);
    }
  }

  function onNext() {
    const btn = $("btnNext");
    const action =
      (btn && btn.dataset.action) || (state.step >= 4 ? "send" : "next");
    if (action === "send" || state.step >= 4) {
      sendToBot();
      return;
    }
    if (!validateStep()) return;
    state.step = Math.min(4, state.step + 1);
    renderBuilder();
    haptic("light");
  }

  function onPrev() {
    collect();
    state.step = Math.max(0, state.step - 1);
    renderBuilder();
  }

  document.body.addEventListener("click", (e) => {
    const tabBtn = e.target.closest(".bf-tab[data-tab]");
    if (tabBtn && tabBtn.dataset.tab) {
      go(tabBtn.dataset.tab);
      return;
    }
    const t = e.target.closest("[data-go]");
    if (t && t.dataset.go) {
      go(t.dataset.go);
      return;
    }
    const cat = e.target.closest("[data-cat]");
    if (cat && cat.dataset.cat) {
      state.cat = cat.dataset.cat;
      renderFilters();
      renderCards();
      haptic("light");
      return;
    }
    const pick = e.target.closest("[data-pick]");
    if (pick && pick.dataset.pick) {
      state.selected = pick.dataset.pick;
      state.step = 0;
      renderCards();
      go("builder");
      toast("قالب انتخاب شد");
      return;
    }
    if (e.target.id === "btnSendBot" || e.target.closest("#btnSendBot")) {
      e.preventDefault();
      sendToBot();
    }
  });

  // Search: HTML id is "q"
  const search = $("q") || $("search");
  if (search) {
    let tmr;
    search.addEventListener("input", () => {
      clearTimeout(tmr);
      tmr = setTimeout(() => {
        state.q = search.value || "";
        renderCards();
      }, 80);
    });
  }

  const btnPrev = $("btnPrev");
  const btnNext = $("btnNext");
  if (btnPrev) {
    btnPrev.addEventListener("click", (e) => {
      e.preventDefault();
      onPrev();
    });
  }
  if (btnNext) {
    btnNext.addEventListener("click", (e) => {
      e.preventDefault();
      onNext();
    });
  }

  const btnTheme = $("btnTheme");
  if (btnTheme) {
    btnTheme.addEventListener("click", () => {
      document.body.classList.toggle("bf-light");
      haptic("soft");
    });
  }
  const btnBrand = $("btnBrand");
  if (btnBrand) {
    btnBrand.addEventListener("click", () => go("showcase"));
  }

  try {
    if (tg && tg.MainButton) tg.MainButton.onClick(() => sendToBot());
    if (tg && tg.BackButton) {
      tg.BackButton.show();
      tg.BackButton.onClick(() => go("catalog"));
    }
  } catch (_) {}

  if (!window.BF_DATA || !Array.isArray(BF_DATA.templates)) {
    toast("خطا در بارگذاری قالب‌ها — data.js لود نشده");
    const cards = $("cards");
    if (cards) {
      cards.innerHTML =
        '<div class="bf-empty">قالب‌ها بارگذاری نشدند. صفحه را رفرش کن یا Deploy را چک کن.</div>';
    }
  } else {
    renderFilters();
    renderCards();
    go("catalog");
    renderBuilder();
  }

  const faq = $("faq");
  if (faq && BF_DATA && BF_DATA.faq) {
    faq.innerHTML = BF_DATA.faq
      .map(
        (f) =>
          `<details class="bf-faq-item"><summary>${esc(
            f.q
          )}</summary><p>${esc(f.a)}</p></details>`
      )
      .join("");
  }
  const gallery = $("gallery");
  if (gallery && BF_DATA && BF_DATA.gallery) {
    gallery.innerHTML = BF_DATA.gallery
      .map((g) => `<div class="bf-g-item">${esc(g)}</div>`)
      .join("");
  }
})();
