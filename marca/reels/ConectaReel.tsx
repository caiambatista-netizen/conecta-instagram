import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadNunito } from "./lib/localFonts";

loadNunito();

// Identidade visual Conecta Terapias
const NAVY = "#12263A";
const SAND = "#FBF7F1";
const GREEN = "#7AC943";
const GREEN_D = "#4CA527";
const BLUE = "#1888CB";
const FONT = "Nunito, sans-serif";

type Theme = "escuro" | "claro";

// Palavra entre *asteriscos* = destaque
export type Scene = {
  theme: Theme;
  seconds: number;
  kind: "title" | "list" | "price";
  eyebrow?: string;
  title: string;
  sub?: string;
  items?: string[];
  price?: string;
  cta?: string;
};

export type ConectaReelProps = { scenes: Scene[] };

const Logo: React.FC<{ size: number }> = ({ size }) => (
  <svg viewBox="0 0 200 206" width={size} height={size * 1.03}>
    <defs>
      <linearGradient id="lb" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#4FCAF2" />
        <stop offset="1" stopColor="#1888CB" />
      </linearGradient>
      <linearGradient id="lg" x1="1" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#95DA46" />
        <stop offset="1" stopColor="#4CA527" />
      </linearGradient>
    </defs>
    <circle cx="44" cy="26" r="18" fill="url(#lb)" />
    <circle cx="156" cy="26" r="18" fill="url(#lg)" />
    <path fill="url(#lb)" fillRule="evenodd" d="M100 68 C93 53 78 40 58 40 C34 40 12 58 12 86 C12 118 38 150 100 196 Z M100 76 C96 67 88 60 77 60 C64 60 52 70 52 86 C52 104 66 122 100 150 Z" />
    <path fill="url(#lg)" fillRule="evenodd" d="M100 68 C107 53 122 40 142 40 C166 40 188 58 188 86 C188 118 162 150 100 196 Z M100 76 C104 67 112 60 123 60 C136 60 148 70 148 86 C148 104 134 122 100 150 Z" />
  </svg>
);

const colors = (t: Theme) =>
  t === "escuro"
    ? { bg: NAVY, text: "#FFFFFF", sub: "rgba(255,255,255,.82)", hi: GREEN, word2: GREEN }
    : { bg: SAND, text: NAVY, sub: "#4a4440", hi: BLUE, word2: GREEN_D };

// Título com palavras entrando uma a uma
const KineticTitle: React.FC<{ text: string; theme: Theme; size: number; delay?: number }> = ({ text, theme, size, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const c = colors(theme);
  const words = text.split(" ");
  let hiOpen = false;
  return (
    <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: size, lineHeight: 1.08, letterSpacing: -2.5, color: c.text, display: "flex", flexWrap: "wrap", columnGap: size * 0.26 }}>
      {words.map((raw, i) => {
        const starts = raw.startsWith("*");
        const ends = raw.endsWith("*") || raw.replace(/[.,!?…]+$/, "").endsWith("*");
        if (starts) hiOpen = true;
        const isHi = hiOpen;
        if (ends) hiOpen = false;
        const w = raw.replace(/\*/g, "");
        const s = spring({ frame: frame - delay - i * 5, fps, config: { damping: 16, stiffness: 90 } });
        return (
          <span key={i} style={{ display: "inline-block", overflow: "hidden", paddingBottom: size * 0.12, marginBottom: -size * 0.12 }}>
            <span style={{ display: "inline-block", transform: `translateY(${(1 - s) * 110}%)`, opacity: s, color: isHi ? c.hi : c.text }}>{w}</span>
          </span>
        );
      })}
    </div>
  );
};

const FadeUp: React.FC<{ delay: number; children: React.ReactNode }> = ({ delay, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 18, stiffness: 90 } });
  return <div style={{ opacity: s, transform: `translateY(${(1 - s) * 40}px)` }}>{children}</div>;
};

const Bar: React.FC = () => {
  const frame = useCurrentFrame();
  const w = interpolate(frame, [0, 14], [0, 170], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return <div style={{ height: 14, width: w, borderRadius: 8, background: "linear-gradient(90deg,#4FCAF2,#1888CB 45%,#95DA46 55%,#4CA527)", marginBottom: 48 }} />;
};

const SceneView: React.FC<{ scene: Scene; total: number }> = ({ scene, total }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const c = colors(scene.theme);
  // entrada: cortina subindo
  const enter = interpolate(frame, [0, 12], [100, 0], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const out = interpolate(frame, [total - 22, total - 14], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ghostRot = interpolate(frame, [0, total], [-6, 6]);
  const ghostY = interpolate(frame, [0, total], [30, -30]);
  const titleWords = scene.title.split(" ").length;
  const afterTitle = 8 + titleWords * 5 + 14;

  return (
    <AbsoluteFill style={{ transform: `translateY(${enter}%)` }}>
      <AbsoluteFill style={{ background: c.bg }} />
      <div style={{ position: "absolute", right: -170, bottom: 160, opacity: 0.06, transform: `rotate(${ghostRot}deg) translateY(${ghostY}px)` }}>
        <Logo size={780} />
      </div>
      <AbsoluteFill style={{ padding: "0 96px", justifyContent: "center", opacity: out }}>
        <Bar />
        {scene.eyebrow && (
          <FadeUp delay={4}>
            <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 48, color: c.word2, marginBottom: 24 }}>{scene.eyebrow}</div>
          </FadeUp>
        )}
        <KineticTitle text={scene.title} theme={scene.theme} size={scene.kind === "list" ? 92 : 104} delay={8} />
        {scene.sub && (
          <FadeUp delay={afterTitle}>
            <div style={{ fontFamily: FONT, fontWeight: 500, fontSize: 50, lineHeight: 1.35, color: c.sub, marginTop: 50 }}>{scene.sub}</div>
          </FadeUp>
        )}
        {scene.items && (
          <div style={{ marginTop: 56, display: "flex", flexDirection: "column", gap: 34 }}>
            {scene.items.map((it, i) => {
              const s = spring({ frame: frame - afterTitle - i * 16, fps, config: { damping: 15, stiffness: 120 } });
              const [num, ...rest] = it.split(" ");
              const isNum = /^\d+$/.test(num);
              return (
                <div key={i} style={{ display: "flex", alignItems: "baseline", gap: 30, opacity: s, transform: `translateX(${(1 - s) * -80}px)`, fontFamily: FONT }}>
                  <span style={{ fontWeight: 800, fontSize: isNum ? 46 : 52, color: c.word2, width: isNum ? 80 : 50 }}>{isNum ? num : "✓"}</span>
                  <span style={{ fontWeight: isNum ? 800 : 700, fontSize: isNum ? 76 : 52, color: c.text }}>{isNum ? rest.join(" ") : it}</span>
                </div>
              );
            })}
          </div>
        )}
        {scene.price && (() => {
          const s = spring({ frame: frame - afterTitle, fps, config: { damping: 9, stiffness: 160 } });
          const pulse = 1 + 0.03 * Math.sin(Math.max(0, frame - afterTitle - 15) / 6);
          const arrow = Math.sin(frame / 5) * 10;
          return (
            <>
              <div style={{ marginTop: 60, alignSelf: "flex-start", transform: `scale(${s * pulse})`, transformOrigin: "left center", fontFamily: FONT, fontWeight: 800, fontSize: 76, color: NAVY, padding: "26px 60px", borderRadius: 999, background: "linear-gradient(90deg,#95DA46,#7AC943)", boxShadow: "0 18px 40px rgba(76,165,39,.28)" }}>
                {scene.price}
              </div>
              <FadeUp delay={afterTitle + 12}>
                <div style={{ marginTop: 40, fontFamily: FONT, fontWeight: 700, fontSize: 46, color: c.sub }}>
                  {scene.cta} <span style={{ display: "inline-block", transform: `translateY(${arrow}px)` }}>👆</span>
                </div>
              </FadeUp>
            </>
          );
        })()}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const ConectaReel: React.FC<ConectaReelProps> = ({ scenes }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  let start = 0;
  const seqs = scenes.map((sc, i) => {
    const dur = Math.round(sc.seconds * fps);
    const el = (
      <Sequence key={i} from={start} durationInFrames={dur + (i < scenes.length - 1 ? 14 : 0)}>
        <SceneView scene={sc} total={dur + 14} />
      </Sequence>
    );
    start += dur;
    return el;
  });
  const cur = (() => {
    let acc = 0;
    for (const sc of scenes) {
      acc += Math.round(sc.seconds * fps);
      if (frame - 9 < acc) return sc.theme;
    }
    return scenes[scenes.length - 1].theme;
  })();
  const logoS = spring({ frame, fps, config: { damping: 12, stiffness: 120 } });
  const prog = frame / durationInFrames;
  const cc = colors(cur);
  return (
    <AbsoluteFill style={{ background: NAVY }}>
      {seqs}
      {/* logo fixo */}
      <div style={{ position: "absolute", top: 170, left: 96, display: "flex", alignItems: "center", gap: 18, transform: `scale(${logoS})`, transformOrigin: "left center" }}>
        <Logo size={72} />
        <div style={{ fontFamily: FONT, fontWeight: 800, lineHeight: 1.02 }}>
          <div style={{ fontSize: 40, color: cc.text, letterSpacing: -1 }}>Conecta</div>
          <div style={{ fontSize: 30, color: cur === "escuro" ? GREEN : GREEN_D }}>Terapias</div>
        </div>
      </div>
      {/* barra de progresso */}
      <div style={{ position: "absolute", top: 110, left: 96, right: 96, height: 6, borderRadius: 4, background: cur === "escuro" ? "rgba(255,255,255,.12)" : "rgba(18,38,58,.10)" }}>
        <div style={{ width: `${prog * 100}%`, height: "100%", borderRadius: 4, background: "linear-gradient(90deg,#4FCAF2,#1888CB 45%,#95DA46 55%,#4CA527)" }} />
      </div>
      <div style={{ position: "absolute", bottom: 300, left: 96, fontFamily: FONT, fontWeight: 800, fontSize: 28, letterSpacing: 3, textTransform: "uppercase", color: cc.text, opacity: 0.5 }}>
        Nós somos a ponte
      </div>
    </AbsoluteFill>
  );
};
