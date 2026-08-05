'use client';

import React, { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

interface GSAPRevealProps {
  children: React.ReactNode;
  className?: string;
  direction?: 'up' | 'down' | 'left' | 'right';
  distance?: number;
  duration?: number;
  delay?: number;
  scrub?: boolean;
  pin?: boolean;
  start?: string;
}

export function GSAPReveal({
  children,
  className = '',
  direction = 'up',
  distance = 60,
  duration = 1,
  delay = 0,
  scrub = false,
  pin = false,
  start = 'top 85%',
}: GSAPRevealProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const dirMap = {
      up: { y: distance, x: 0 },
      down: { y: -distance, x: 0 },
      left: { x: distance, y: 0 },
      right: { x: -distance, y: 0 },
    };

    const fromVars = {
      opacity: 0,
      ...dirMap[direction],
    };

    const toVars = {
      opacity: 1,
      x: 0,
      y: 0,
      duration,
      delay,
      ease: 'power3.out',
    };

    if (scrub) {
      Object.assign(toVars, { scrub: 0.5 });
    }

    const tween = gsap.fromTo(el, fromVars, {
      ...toVars,
      scrollTrigger: {
        trigger: el,
        start,
        end: pin ? '+=500' : undefined,
        toggleActions: 'play none none reverse',
        pin,
      },
    });

    return () => {
      tween.scrollTrigger?.kill();
      tween.kill();
    };
  }, [direction, distance, duration, delay, scrub, pin, start]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}

interface GSAPStaggerProps {
  children: React.ReactNode;
  className?: string;
  stagger?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  distance?: number;
}

export function GSAPStagger({
  children,
  className = '',
  stagger = 0.1,
  direction = 'up',
  distance = 40,
}: GSAPStaggerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const children = Array.from(container.children) as HTMLElement[];
    if (children.length === 0) return;

    const dirMap = {
      up: { y: distance },
      down: { y: -distance },
      left: { x: distance },
      right: { x: -distance },
    };

    const tween = gsap.fromTo(
      children,
      { opacity: 0, ...dirMap[direction] },
      {
        opacity: 1,
        x: 0,
        y: 0,
        duration: 0.8,
        stagger,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: container,
          start: 'top 80%',
          toggleActions: 'play none none reverse',
        },
      }
    );

    return () => {
      tween.scrollTrigger?.kill();
      tween.kill();
    };
  }, [stagger, direction, distance]);

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  );
}

interface GSAPParallaxProps {
  children: React.ReactNode;
  className?: string;
  speed?: number;
}

export function GSAPParallax({ children, className = '', speed = 0.3 }: GSAPParallaxProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const tween = gsap.to(el, {
      yPercent: speed * 100,
      ease: 'none',
      scrollTrigger: {
        trigger: el,
        start: 'top bottom',
        end: 'bottom top',
        scrub: true,
      },
    });

    return () => {
      tween.scrollTrigger?.kill();
      tween.kill();
    };
  }, [speed]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}

interface GSAPTextRevealProps {
  text: string;
  className?: string;
  tag?: 'h1' | 'h2' | 'h3' | 'p';
  delay?: number;
}

export function GSAPTextReveal({ text, className = '', tag: Tag = 'h2', delay = 0 }: GSAPTextRevealProps) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const chars = el.querySelectorAll('.char');

    const tween = gsap.fromTo(
      chars,
      { opacity: 0, y: 20, rotateX: -90 },
      {
        opacity: 1,
        y: 0,
        rotateX: 0,
        duration: 0.6,
        stagger: 0.02,
        delay,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: el,
          start: 'top 85%',
          toggleActions: 'play none none reverse',
        },
      }
    );

    return () => {
      tween.scrollTrigger?.kill();
      tween.kill();
    };
  }, [text, delay]);

  return (
    // @ts-ignore
    <Tag ref={ref} className={className} style={{ perspective: '1000px' }}>
      {text.split('').map((char, i) => (
        <span key={i} className="char inline-block" style={{ transformOrigin: 'bottom' }}>
          {char === ' ' ? '\u00A0' : char}
        </span>
      ))}
    </Tag>
  );
}

interface GSAPCountUpProps {
  value: number;
  suffix?: string;
  prefix?: string;
  className?: string;
}

export function GSAPCountUp({ value, suffix = '', prefix = '', className = '' }: GSAPCountUpProps) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const obj = { val: 0 };

    const tween = gsap.to(obj, {
      val: value,
      duration: 2,
      ease: 'power2.out',
      onUpdate: () => {
        el.textContent = `${prefix}${Math.round(obj.val).toLocaleString('en-IN')}${suffix}`;
      },
      scrollTrigger: {
        trigger: el,
        start: 'top 85%',
        toggleActions: 'play none none reverse',
      },
    });

    return () => {
      tween.scrollTrigger?.kill();
      tween.kill();
    };
  }, [value, suffix, prefix]);

  return <span ref={ref} className={className}>{prefix}0{suffix}</span>;
}
