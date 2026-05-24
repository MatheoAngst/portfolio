const body = document.body;
const menuButton = document.querySelector(".menu-button");
const menuOverlay = document.querySelector(".menu-overlay");
const menuLinks = document.querySelectorAll("[data-menu-link]");
const progressBar = document.querySelector(".page-progress span");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const desktopMedia = window.matchMedia("(min-width: 1025px)");
let menuUnlockTimer;
let refreshTimer;

const getProjectDestination = (target) => {
if (window.ScrollTrigger) {
const linkedTrigger = ScrollTrigger.getAll().find((trigger) => trigger.trigger === target && trigger.pin);
if (linkedTrigger) {
return linkedTrigger.start;
}
}
return target.getBoundingClientRect().top + window.scrollY;
};

const openMenu = () => {
clearTimeout(menuUnlockTimer);
body.classList.add("menu-open");
menuButton.setAttribute("aria-expanded", "true");
menuOverlay.setAttribute("aria-hidden", "false");
};

const closeMenu = () => {
body.classList.remove("menu-open");
menuButton.setAttribute("aria-expanded", "false");
menuOverlay.setAttribute("aria-hidden", "true");
clearTimeout(menuUnlockTimer);
menuUnlockTimer = setTimeout(() => {
body.classList.remove("menu-open");
}, 460);
};

menuButton.addEventListener("click", () => {
if (body.classList.contains("menu-open")) {
closeMenu();
} else {
openMenu();
}
});

menuLinks.forEach((link) => {
link.addEventListener("click", (event) => {
event.preventDefault();
const target = document.querySelector(link.getAttribute("href"));
closeMenu();
if (target) {
requestAnimationFrame(() => {
const destination = Math.max(0, Math.round(getProjectDestination(target)));
menuLinks.forEach((item) => {
item.classList.toggle("is-active", item === link);
});
if (window.gsap && window.ScrollToPlugin && !prefersReducedMotion) {
gsap.killTweensOf(window);
gsap.to(window, {
duration: 0.78,
ease: "power3.inOut",
scrollTo: {
y: destination,
autoKill: false
}
});
} else {
window.scrollTo({
top: destination,
behavior: prefersReducedMotion ? "auto" : "smooth"
});
}
});
}
});
});

window.addEventListener("keydown", (event) => {
if (event.key === "Escape" && body.classList.contains("menu-open")) {
closeMenu();
}
});

window.addEventListener("pageshow", () => {
closeMenu();
});

const updateProgress = () => {
const max = document.documentElement.scrollHeight - window.innerHeight;
const progress = max <= 0 ? 0 : window.scrollY / max;
progressBar.style.width = `${Math.min(1, Math.max(0, progress)) * 100}%`;
};

window.addEventListener("scroll", updateProgress, { passive: true });
window.addEventListener("resize", () => {
updateProgress();
clearTimeout(refreshTimer);
refreshTimer = setTimeout(() => {
if (desktopMedia.matches && window.ScrollTrigger) {
ScrollTrigger.refresh();
}
}, 160);
});
updateProgress();

const sectionObserver = new IntersectionObserver((entries) => {
entries.forEach((entry) => {
if (entry.isIntersecting) {
const id = entry.target.getAttribute("id");
menuLinks.forEach((link) => {
link.classList.toggle("is-active", link.getAttribute("href") === `#${id}`);
});
}
});
}, {
threshold: 0.38
});

document.querySelectorAll(".project-section").forEach((section) => {
sectionObserver.observe(section);
});

if (window.gsap && window.ScrollTrigger && !prefersReducedMotion) {
if (window.ScrollToPlugin) {
gsap.registerPlugin(ScrollTrigger, ScrollToPlugin);
} else {
gsap.registerPlugin(ScrollTrigger);
}

const mm = gsap.matchMedia();

mm.add("(min-width: 1025px)", () => {
body.classList.add("gsap-horizontal");

gsap.utils.toArray(".project-card").forEach((card) => {
gsap.fromTo(card, {
y: 58,
scale: 0.965
}, {
y: 0,
scale: 1,
duration: 0.9,
ease: "power3.out",
scrollTrigger: {
trigger: card,
start: "top 82%"
}
});
});

gsap.utils.toArray(".project-tags span").forEach((tag) => {
gsap.fromTo(tag, {
y: 14
}, {
y: 0,
duration: 0.48,
ease: "power2.out",
scrollTrigger: {
trigger: tag.closest(".project-card"),
start: "top 78%"
}
});
});

gsap.utils.toArray(".project-section .text-zone p").forEach((paragraph) => {
gsap.fromTo(paragraph, {
y: 26,
opacity: 0
}, {
y: 0,
opacity: 1,
duration: 0.72,
ease: "power3.out",
scrollTrigger: {
trigger: paragraph,
start: "top 90%"
}
});
});

gsap.utils.toArray(".project-section-horizontal").forEach((section) => {
const pinWrap = section.querySelector(".pin-wrap");
const card = section.querySelector(".horizontal-card");
const track = section.querySelector(".horizontal-track");
const panels = gsap.utils.toArray(section.querySelectorAll(".project-panel"));

const getDistance = () => Math.max(0, track.scrollWidth - card.clientWidth);

gsap.set(track, {
x: 0
});

const tween = gsap.to(track, {
x: () => -getDistance(),
ease: "none",
scrollTrigger: {
trigger: section,
pin: pinWrap,
start: "top top",
end: () => `+=${getDistance() + window.innerHeight * 0.72}`,
scrub: 1,
invalidateOnRefresh: true,
anticipatePin: 1
}
});

panels.forEach((panel, index) => {
gsap.fromTo(panel, {
opacity: index === 0 ? 1 : 0.68,
scale: index === 0 ? 1 : 0.985
}, {
opacity: 1,
scale: 1,
ease: "none",
scrollTrigger: {
containerAnimation: tween,
trigger: panel,
start: "left 70%",
end: "right 62%",
scrub: true
}
});
});
});

return () => {
body.classList.remove("gsap-horizontal");
gsap.set(".horizontal-track", {
clearProps: "transform,willChange"
});
};
});

mm.add("(max-width: 1024px)", () => {
body.classList.remove("gsap-horizontal");
gsap.set(".horizontal-track", {
clearProps: "transform,willChange"
});
});

window.addEventListener("load", () => {
if (desktopMedia.matches) {
ScrollTrigger.refresh();
}
});
}
