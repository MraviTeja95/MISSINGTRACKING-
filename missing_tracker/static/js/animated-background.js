(function() {
    const backgroundNode = document.querySelector('.app-background');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const liquidWrap = document.querySelector('.app-background__liquid-wrap');
    const liquidNode = document.querySelector('.app-background__liquid');
    const noiseNode = document.querySelector('.app-background__noise');
    const turbulenceNode = document.getElementById('bg-turbulence');
    const hueRotateNode = document.getElementById('bg-hue-rotate');
    const displacementNodeA = document.getElementById('bg-displacement-a');
    const displacementNodeB = document.getElementById('bg-displacement-b');

    if (!backgroundNode || !liquidWrap || !liquidNode || !noiseNode || !turbulenceNode || !hueRotateNode || !displacementNodeA || !displacementNodeB) return;

    const mapRange = (value, fromLow, fromHigh, toLow, toHigh) => {
        if (fromLow === fromHigh) return toLow;
        const percentage = (value - fromLow) / (fromHigh - fromLow);
        return toLow + percentage * (toHigh - toLow);
    };

    const config = {
        sizing: 'fill',
        color: 'rgba(128, 128, 128, 1)',
        animation: {
            scale: 62,
            speed: 60
        },
        noise: {
            opacity: 0.16,
            scale: 1
        }
    };

    const animationScale = config.animation.scale;
    const animationSpeed = config.animation.speed;
    const displacementScale = mapRange(animationScale, 1, 100, 20, 100);
    const animationDuration = mapRange(animationSpeed, 1, 100, 1000, 50) / 25;
    const turbulenceX = mapRange(animationScale, 0, 100, 0.001, 0.0005);
    const turbulenceY = mapRange(animationScale, 0, 100, 0.004, 0.002);

    liquidWrap.style.inset = `${Math.round(-displacementScale)}px`;
    liquidNode.style.backgroundColor = config.color;
    liquidNode.style.maskSize = config.sizing === 'stretch' ? '100% 100%' : 'cover';
    liquidNode.style.webkitMaskSize = config.sizing === 'stretch' ? '100% 100%' : 'cover';
    noiseNode.style.backgroundSize = `${config.noise.scale * 200}px`;
    noiseNode.style.opacity = String(config.noise.opacity / 2);

    if (prefersReducedMotion) {
        displacementNodeA.setAttribute('scale', '0');
        displacementNodeB.setAttribute('scale', '0');
        hueRotateNode.setAttribute('values', '180');
        return;
    }

    let rafId = null;
    let startTime = performance.now();

    const tick = (now) => {
        const elapsed = (now - startTime) / 1000;
        const loopProgress = (elapsed % animationDuration) / animationDuration;
        const hueRotate = loopProgress * 360;

        turbulenceNode.setAttribute('baseFrequency', `${turbulenceX.toFixed(4)} ${turbulenceY.toFixed(4)}`);
        hueRotateNode.setAttribute('values', hueRotate.toFixed(2));
        displacementNodeA.setAttribute('scale', displacementScale.toFixed(1));
        displacementNodeB.setAttribute('scale', displacementScale.toFixed(1));
        rafId = window.requestAnimationFrame(tick);
    };

    const start = () => {
        if (rafId !== null) return;
        startTime = performance.now();
        rafId = window.requestAnimationFrame(tick);
    };

    const stop = () => {
        if (rafId === null) return;
        window.cancelAnimationFrame(rafId);
        rafId = null;
    };

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            stop();
        } else {
            start();
        }
    });

    window.addEventListener('beforeunload', stop);
    start();
})();
