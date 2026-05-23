gsap.registerPlugin(ScrollTrigger);

gsap.from(".hero > *", {
    y: 50,
    opacity: 0,
    duration: 1,
    stagger: 0.2,
    ease: "power4.out"
});

gsap.from(".skill-card", {
    scrollTrigger: {
        trigger: ".skills",
        start: "top 80%"
    },
    y: 100,
    opacity: 0,
    duration: 1,
    stagger: 0.2
});

gsap.to(".timeline-line", {
    scrollTrigger: {
        trigger: ".timeline-container",
        start: "top center",
        end: "bottom center",
        scrub: true
    },
    height: "100%"
});

gsap.from(".timeline-item", {
    scrollTrigger: {
        trigger: ".timeline-container",
        start: "top 80%"
    },
    x: -50,
    opacity: 0,
    duration: 0.8,
    stagger: 0.2
});

gsap.from(".project-card", {
    scrollTrigger: {
        trigger: ".projects-section",
        start: "top 80%"
    },
    scale: 0.9,
    opacity: 0,
    duration: 0.6,
    stagger: 0.1
});