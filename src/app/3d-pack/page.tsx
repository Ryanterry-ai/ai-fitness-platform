'use client';

import React, { useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Box,
  Palette,
  Sun,
  Camera,
  Download,
  Globe,
  Instagram,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  Zap,
  Maximize2,
  ArrowRight,
  Check,
  Image as ImageIcon,
  Layers,
  Sparkles,
} from 'lucide-react';
import PackCanvas, { CAMERA_PRESETS } from '@/components/PackCanvas';

const EASE = [0.23, 1, 0.32, 1] as const;

/* ─────────────────────────────────────────────
   PIPELINE STEPS
   ───────────────────────────────────────────── */

const PIPELINE_STEPS = [
  { id: 'jar', label: 'Prime X Jar', icon: Box, desc: '3D jar model' },
  { id: 'labels', label: 'Labels', icon: Palette, desc: 'Flavour labels' },
  { id: 'studio', label: 'HDR Studio', icon: Sun, desc: 'Lighting setup' },
  { id: 'angles', label: 'Render Angles', icon: Camera, desc: '18 camera presets' },
  { id: 'export', label: 'Export', icon: Download, desc: 'Website + Instagram' },
];

const FLAVOURS = [
  { id: 'Orange', color: '#FF6B00', emoji: '🍊' },
  { id: 'Fruit Punch', color: '#FF1744', emoji: '🍹' },
  { id: 'Rocket Lollipop', color: '#7C4DFF', emoji: '🚀' },
] as const;

const LIGHT_PRESETS = [
  { id: 'studio' as const, label: 'Studio', desc: 'Clean, professional', icon: '💡' },
  { id: 'dramatic' as const, label: 'Dramatic', desc: 'Bold, golden', icon: '🔥' },
  { id: 'soft' as const, label: 'Soft', desc: 'Gentle, natural', icon: '☀️' },
  { id: 'neon' as const, label: 'Neon', desc: 'Cyberpunk glow', icon: '💜' },
];

const EXPORT_FORMATS = [
  { id: 'website-hero', label: 'Website Hero', width: 1920, height: 1080, format: 'website' as const, icon: Globe },
  { id: 'website-card', label: 'Website Card', width: 800, height: 600, format: 'website' as const, icon: Globe },
  { id: 'ig-post', label: 'Instagram Post', width: 1080, height: 1080, format: 'instagram' as const, icon: Instagram },
  { id: 'ig-story', label: 'Instagram Story', width: 1080, height: 1920, format: 'instagram' as const, icon: Instagram },
  { id: 'ig-reel', label: 'Reels Cover', width: 1080, height: 1920, format: 'instagram' as const, icon: Instagram },
];

/* ─────────────────────────────────────────────
   PIPELINE VISUALIZATION
   ───────────────────────────────────────────── */

function PipelineViz({ activeStep }: { activeStep: number }) {
  return (
    <div className="flex items-center justify-center gap-1 sm:gap-2 mb-8 overflow-x-auto pb-2">
      {PIPELINE_STEPS.map((step, i) => (
        <React.Fragment key={step.id}>
          <motion.div
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
              i === activeStep
                ? 'bg-pure-yellow text-pure-black'
                : i < activeStep
                ? 'bg-pure-yellow/20 text-pure-yellow'
                : 'bg-white/5 text-gray-500'
            }`}
            animate={{ scale: i === activeStep ? 1.05 : 1 }}
          >
            <step.icon className="w-4 h-4" />
            <span className="hidden sm:inline">{step.label}</span>
          </motion.div>
          {i < PIPELINE_STEPS.length - 1 && (
            <ArrowRight className={`w-4 h-4 shrink-0 ${i < activeStep ? 'text-pure-yellow' : 'text-gray-600'}`} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

/* ─────────────────────────────────────────────
   MAIN PAGE
   ───────────────────────────────────────────── */

export default function Pack3DPage() {
  const [flavour, setFlavour] = useState('Orange');
  const [lightPreset, setLightPreset] = useState<'studio' | 'dramatic' | 'soft' | 'neon'>('studio');
  const [activeCameraPreset, setActiveCameraPreset] = useState<number | null>(0);
  const [autoRotate, setAutoRotate] = useState(true);
  const [exportFormat, setExportFormat] = useState('website-hero');
  const [isExporting, setIsExporting] = useState(false);
  const [exportDone, setExportDone] = useState(false);
  const [showAngles, setShowAngles] = useState(false);
  const [filterFormat, setFilterFormat] = useState<'all' | 'website' | 'instagram'>('all');

  const currentPreset = activeCameraPreset !== null ? CAMERA_PRESETS[activeCameraPreset] : null;

  const filteredPresets = CAMERA_PRESETS.filter(
    (p) => filterFormat === 'all' || p.format === filterFormat
  );

  const handleExport = useCallback(() => {
    const canvas = document.querySelector('canvas') as HTMLCanvasElement | null;
    if (!canvas) return;

    setIsExporting(true);
    setAutoRotate(false);

    // Wait for render to settle
    setTimeout(() => {
      try {
        const dataUrl = canvas.toDataURL('image/png', 1.0);
        const link = document.createElement('a');
        link.download = `PURE-${flavour.replace(/\s/g, '-')}-${lightPreset}-${EXPORT_FORMATS.find(f => f.id === exportFormat)?.label.replace(/\s/g, '-') || 'render'}.png`;
        link.href = dataUrl;
        link.click();
        setExportDone(true);
        setTimeout(() => setExportDone(false), 3000);
      } catch (e) {
        console.error('Export failed:', e);
      }
      setIsExporting(false);
    }, 500);
  }, [flavour, lightPreset, exportFormat]);

  return (
    <div className="bg-pure-black min-h-screen pt-24 pb-20">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: EASE }}
        >
          <span className="inline-flex items-center gap-2 bg-pure-yellow/10 border border-pure-yellow/20 rounded-full px-4 py-1.5 mb-4">
            <Sparkles className="w-3.5 h-3.5 text-pure-yellow" />
            <span className="text-[11px] font-bold text-pure-yellow uppercase tracking-wider">3D Render Pipeline</span>
          </span>
          <h1 className="text-5xl sm:text-7xl font-black uppercase tracking-tighter">
            PURE <span className="text-pure-yellow">MASTER 3D PACK</span>
          </h1>
          <p className="text-gray-500 mt-3 max-w-2xl mx-auto text-sm">
            Jar → Labels → HDR Studio → Unlimited Angles → Website + Instagram
          </p>
        </motion.div>

        {/* Pipeline Visualization */}
        <PipelineViz activeStep={2} />

        <div className="grid lg:grid-cols-[1fr_380px] gap-6">
          {/* Left: 3D Canvas */}
          <div className="space-y-4">
            {/* Canvas */}
            <div className="rounded-3xl overflow-hidden border border-white/10 bg-pure-dark">
              <PackCanvas
                flavour={flavour}
                lightPreset={lightPreset}
                cameraPreset={currentPreset}
                autoRotate={autoRotate}
                className="aspect-[16/10] w-full"
              />
            </div>

            {/* Camera Presets Grid */}
            <div className="glass rounded-2xl border border-white/10 p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Camera className="w-4 h-4 text-pure-yellow" />
                  <span className="text-sm font-bold text-white">Camera Angles</span>
                  <span className="text-[10px] text-gray-500 bg-white/5 px-2 py-0.5 rounded-full">{filteredPresets.length} presets</span>
                </div>
                <div className="flex gap-1">
                  {(['all', 'website', 'instagram'] as const).map((f) => (
                    <button
                      key={f}
                      onClick={() => setFilterFormat(f)}
                      className={`px-3 py-1 rounded-lg text-[10px] font-bold uppercase transition-all ${
                        filterFormat === f ? 'bg-pure-yellow text-pure-black' : 'bg-white/5 text-gray-500 hover:text-white'
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-6 gap-2">
                {filteredPresets.map((preset) => {
                  const idx = CAMERA_PRESETS.indexOf(preset);
                  const isActive = activeCameraPreset === idx;
                  return (
                    <motion.button
                      key={preset.name}
                      onClick={() => {
                        setActiveCameraPreset(idx);
                        setAutoRotate(false);
                      }}
                      className={`p-2 rounded-xl text-center transition-all ${
                        isActive
                          ? 'bg-pure-yellow text-pure-black'
                          : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                      }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <p className="text-[10px] font-bold leading-tight">{preset.name}</p>
                      <p className="text-[8px] opacity-60 mt-0.5">{preset.position.map(v => Math.round(v)).join(', ')}</p>
                    </motion.button>
                  );
                })}
              </div>

              {/* Auto rotate toggle */}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/10">
                <button
                  onClick={() => { setAutoRotate(!autoRotate); setActiveCameraPreset(null); }}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    autoRotate ? 'bg-pure-yellow text-pure-black' : 'bg-white/5 text-gray-500'
                  }`}
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Auto Rotate
                </button>
                <span className="text-[10px] text-gray-600">
                  Drag to orbit • Scroll to zoom
                </span>
              </div>
            </div>
          </div>

          {/* Right: Controls Panel */}
          <div className="space-y-4">
            {/* Flavour Selector */}
            <div className="glass rounded-2xl border border-white/10 p-5">
              <div className="flex items-center gap-2 mb-4">
                <Palette className="w-4 h-4 text-pure-yellow" />
                <span className="text-sm font-bold text-white">1. Select Label</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {FLAVOURS.map((f) => (
                  <motion.button
                    key={f.id}
                    onClick={() => setFlavour(f.id)}
                    className={`relative p-3 rounded-xl border-2 text-center transition-all ${
                      flavour === f.id
                        ? 'border-pure-yellow bg-pure-yellow/10'
                        : 'border-white/10 bg-white/5 hover:border-white/30'
                    }`}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                  >
                    <span className="text-2xl block mb-1">{f.emoji}</span>
                    <span className="text-[10px] font-bold text-white block">{f.id}</span>
                    <div className="w-full h-1 rounded-full mt-2" style={{ background: f.color }} />
                    {flavour === f.id && (
                      <motion.div
                        className="absolute top-1.5 right-1.5 w-4 h-4 bg-pure-yellow rounded-full flex items-center justify-center"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                      >
                        <Check className="w-2.5 h-2.5 text-pure-black" />
                      </motion.div>
                    )}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Lighting */}
            <div className="glass rounded-2xl border border-white/10 p-5">
              <div className="flex items-center gap-2 mb-4">
                <Sun className="w-4 h-4 text-pure-yellow" />
                <span className="text-sm font-bold text-white">2. HDR Studio</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {LIGHT_PRESETS.map((lp) => (
                  <motion.button
                    key={lp.id}
                    onClick={() => setLightPreset(lp.id)}
                    className={`p-3 rounded-xl border-2 text-left transition-all ${
                      lightPreset === lp.id
                        ? 'border-pure-yellow bg-pure-yellow/10'
                        : 'border-white/10 bg-white/5 hover:border-white/30'
                    }`}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                  >
                    <span className="text-lg block">{lp.icon}</span>
                    <span className="text-xs font-bold text-white block mt-1">{lp.label}</span>
                    <span className="text-[10px] text-gray-500">{lp.desc}</span>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Export */}
            <div className="glass rounded-2xl border border-white/10 p-5">
              <div className="flex items-center gap-2 mb-4">
                <Download className="w-4 h-4 text-pure-yellow" />
                <span className="text-sm font-bold text-white">3. Export Render</span>
              </div>

              <div className="space-y-2 mb-4">
                {EXPORT_FORMATS.map((fmt) => (
                  <button
                    key={fmt.id}
                    onClick={() => setExportFormat(fmt.id)}
                    className={`w-full p-3 rounded-xl border-2 text-left flex items-center gap-3 transition-all ${
                      exportFormat === fmt.id
                        ? 'border-pure-yellow bg-pure-yellow/10'
                        : 'border-white/10 bg-white/5 hover:border-white/30'
                    }`}
                  >
                    <fmt.icon className="w-4 h-4 text-pure-yellow shrink-0" />
                    <div className="flex-1">
                      <span className="text-xs font-bold text-white block">{fmt.label}</span>
                      <span className="text-[10px] text-gray-500">{fmt.width}×{fmt.height}px</span>
                    </div>
                    {exportFormat === fmt.id && <Check className="w-4 h-4 text-pure-yellow shrink-0" />}
                  </button>
                ))}
              </div>

              <motion.button
                onClick={handleExport}
                disabled={isExporting}
                className={`w-full py-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                  exportDone
                    ? 'bg-green-500 text-white'
                    : 'bg-pure-yellow text-pure-black hover:bg-pure-yellow-light'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {isExporting ? (
                  <>
                    <motion.div
                      className="w-4 h-4 border-2 border-pure-black border-t-transparent rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    />
                    Rendering...
                  </>
                ) : exportDone ? (
                  <>
                    <Check className="w-4 h-4" /> Downloaded!
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" /> Export PNG
                  </>
                )}
              </motion.button>

              <p className="text-[10px] text-gray-600 text-center mt-2">
                Renders current viewport at 2× resolution
              </p>
            </div>

            {/* Quick Summary */}
            <div className="glass rounded-2xl border border-white/10 p-5">
              <div className="flex items-center gap-2 mb-3">
                <Layers className="w-4 h-4 text-pure-yellow" />
                <span className="text-sm font-bold text-white">Current Render</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">Label</span>
                  <span className="text-white font-bold">{flavour}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Lighting</span>
                  <span className="text-white font-bold capitalize">{lightPreset}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Camera</span>
                  <span className="text-white font-bold">{currentPreset?.name || 'Free Orbit'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Export</span>
                  <span className="text-white font-bold">{EXPORT_FORMATS.find(f => f.id === exportFormat)?.label}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
