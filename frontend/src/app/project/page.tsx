"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { motion, useScroll, useSpring } from "framer-motion";
import { 
  FileText, 
  Image as ImageIcon, 
  ChevronRight, 
  ExternalLink,
  Code2,
  Cpu,
  Palette,
  AlertTriangle,
  CheckCircle2,
  Menu,
  X,
  ArrowUpRight
} from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// --- Components ---

const Section = ({ id, children, className }: { id: string; children: React.ReactNode; className?: string }) => (
  <section id={id} className={cn("scroll-mt-24", className)}>
    {children}
  </section>
);

const SectionHeading = ({ children, icon: Icon }: { children: React.ReactNode; icon?: React.ElementType }) => (
  <h2 className="text-3xl font-bold text-slate-900 mb-8 flex items-center gap-3 border-b border-slate-200 pb-4">
    {Icon && <Icon className="w-8 h-8 text-indigo-600" />}
    <span className="bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700">
      {children}
    </span>
  </h2>
);

const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={cn("bg-white rounded-2xl p-6 shadow-sm border border-slate-200/60 hover:shadow-md transition-shadow duration-300", className)}>
    {children}
  </div>
);

const Badge = ({ children, variant = "default" }: { children: React.ReactNode; variant?: "default" | "success" | "warning" | "danger" }) => {
  const variants = {
    default: "bg-slate-100 text-slate-700 border-slate-200",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    danger: "bg-rose-50 text-rose-700 border-rose-200",
  };
  return (
    <span className={cn("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border", variants[variant])}>
      {children}
    </span>
  );
};

// --- Main Page ---

export default function ProjectPage() {
  const [activeSection, setActiveSection] = useState("home");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  });

  const navItems = [
    { id: "home", label: "Home" },
    { id: "abstract", label: "Abstract" },
    { id: "intro", label: "Introduction" },
    { id: "method", label: "Methodology" },
    { id: "celeb", label: "CelebHQ Results" },
    { id: "coco", label: "COCO Results" },
    { id: "discussion", label: "Discussion" },
  ];

  useEffect(() => {
    const handleScroll = () => {
      const sections = navItems.map(item => document.getElementById(item.id));
      const scrollPosition = window.scrollY + 150;

      for (const section of sections) {
        if (section && section.offsetTop <= scrollPosition && (section.offsetTop + section.offsetHeight) > scrollPosition) {
          setActiveSection(section.id);
          break;
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setActiveSection(id);
      setIsMobileMenuOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-indigo-100 selection:text-indigo-900">
      
      {/* Scroll Progress Bar */}
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-indigo-600 origin-left z-50"
        style={{ scaleX }}
      />

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => scrollToSection("home")}>
              <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">
                P
              </div>
              <span className="font-bold text-slate-900 hidden sm:block">PixelArena</span>
            </div>

            {/* Desktop Nav */}
            <div className="hidden md:flex space-x-1">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className={cn(
                    "px-3 py-2 rounded-md text-sm font-medium transition-all duration-200",
                    activeSection === item.id
                      ? "bg-indigo-50 text-indigo-700 shadow-sm"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  )}
                >
                  {item.label}
                </button>
              ))}
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="text-slate-600 hover:text-slate-900 p-2"
              >
                {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Nav */}
        {isMobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden bg-white border-b border-slate-200"
          >
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className={cn(
                    "block px-3 py-2 rounded-md text-base font-medium w-full text-left",
                    activeSection === item.id
                      ? "bg-indigo-50 text-indigo-700"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  )}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </nav>

      {/* Hero Section */}
      <div id="home" className="relative pt-32 pb-20 sm:pt-40 sm:pb-24 overflow-hidden">
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-[radial-gradient(#e0e7ff_1px,transparent_1px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-50" />
          <div className="absolute top-0 right-0 -translate-y-12 translate-x-12 blur-3xl opacity-30">
             <div className="aspect-[1097/845] w-[68.5625rem] bg-gradient-to-tr from-[#ff4694] to-[#776fff] clip-path-polygon" style={{ clipPath: "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)" }}></div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* IJCAI Badge removed
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-sm font-medium mb-8">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
              </span>
              IJCAI 2026 Submission
            </span>
            */}
            
            <h1 className="text-5xl sm:text-7xl font-bold tracking-tight text-slate-900 mb-6 mt-8">
              Pixel<span className="text-indigo-600">Arena</span>
            </h1>
            <p className="text-xl sm:text-2xl text-slate-600 max-w-2xl mx-auto font-light leading-relaxed">
              A Benchmark for <span className="font-semibold text-slate-900">Pixel-Precision Visual Intelligence</span> in Omni-Modal Models
            </p>

            <div className="mt-10 flex flex-wrap justify-center gap-4">
              <a href="/" className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-900 text-white font-medium hover:bg-slate-800 transition-colors shadow-lg hover:shadow-xl hover:-translate-y-0.5 transform duration-200">
                <ImageIcon size={20} />
                View Gallery
              </a>
              <button disabled className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white text-slate-400 font-medium border border-slate-200 cursor-not-allowed">
                <FileText size={20} />
                Paper (Coming Soon)
              </button>
              <button disabled className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white text-slate-400 font-medium border border-slate-200 cursor-not-allowed">
                <svg width={20} height={20} viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
                Code (Coming Soon)
              </button>
            </div>
          </motion.div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-24 pb-32">
        
        {/* Abstract */}
        <Section id="abstract">
          <Card className="bg-gradient-to-br from-white to-slate-50 border-slate-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-indigo-100 rounded-lg text-indigo-600">
                <FileText size={24} />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">Abstract</h2>
            </div>
            <p className="text-lg text-slate-700 leading-8 font-serif text-justify">
              Omni-modal models that have multimodal input and output are emerging. However, benchmarking their multimodal generation, especially in image generation, is challenging due to the subtleties of human preferences and model biases. Many image generation benchmarks focus on aesthetics instead of the fine-grained generation capabilities of these models, failing to evaluate their visual intelligence with objective metrics. In <strong>PixelArena</strong>, we propose using semantic segmentation tasks to objectively examine their fine-grained generative intelligence with pixel precision.
            </p>
            <p className="text-lg text-slate-700 leading-8 font-serif text-justify mt-4">
              With our benchmark and experiments, we find the latest <strong>Gemini 3 Pro Image</strong> has emergent image generation capabilities that generate semantic masks with high fidelity under zero-shot settings, showcasing visual intelligence unseen before and true generalization in new image generation tasks. We further investigate its results, compare them qualitatively and quantitatively with those of other models, and present failure cases.
            </p>
          </Card>
        </Section>

        {/* Introduction */}
        <Section id="intro">
          <SectionHeading icon={ArrowUpRight}>Introduction</SectionHeading>
          
          <div className="prose prose-lg prose-slate max-w-none font-serif">
            <p>
              Since the release of GPT-4o, <em>omni-modal models (OMMs)</em>—which have multiple input and output modalities—have been a focus of research. While much focus has been placed on aesthetics, few have quantitatively examined the <strong>precision and generalizability</strong> of the image generation capabilities.
            </p>
            <p>
              In <strong>PixelArena</strong>, we propose using pixel-level tasks—specifically semantic segmentation tasks—to examine OMMs' fine-grained control capability, which we term <span className="text-indigo-700 font-semibold bg-indigo-50 px-1 rounded">Pixel-Precision Visual Intelligence (PPVI)</span>.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mt-10">
            {[
              { title: "PixelArena Benchmark", desc: "A benchmark using semantic segmentation to measure fine-grained control.", icon: CheckCircle2, color: "text-emerald-600", bg: "bg-emerald-50" },
              { title: "Emergent Zero-Shot", desc: "Revealing surprising zero-shot capabilities in Gemini 3 Pro Image.", icon: Cpu, color: "text-blue-600", bg: "bg-blue-50" },
              { title: "Failure Analysis", desc: "In-depth qualitative and quantitative analysis of failure modes.", icon: AlertTriangle, color: "text-amber-600", bg: "bg-amber-50" }
            ].map((item, i) => (
              <Card key={i} className="hover:-translate-y-1 transition-transform">
                <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center mb-4", item.bg, item.color)}>
                  <item.icon size={24} />
                </div>
                <h3 className="font-bold text-lg text-slate-900 mb-2">{item.title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">{item.desc}</p>
              </Card>
            ))}
          </div>
        </Section>

        {/* Methodology */}
        <Section id="method">
          <SectionHeading icon={Code2}>Methodology</SectionHeading>
          
          <div className="grid lg:grid-cols-2 gap-10 items-start">
            <div className="space-y-8">
              <div>
                <h3 className="text-xl font-bold text-slate-900 mb-3 flex items-center gap-2">
                  <span className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-sm font-bold text-slate-600">1</span>
                  Datasets
                </h3>
                <p className="text-slate-600 leading-relaxed mb-4">
                  We use the <strong>COCO</strong> and <strong>CelebAMask-HQ</strong> datasets. We randomly sampled 150 images and their corresponding masks from each dataset.
                </p>
                <div className="flex gap-2">
                  <Badge>COCO (150 images)</Badge>
                  <Badge>CelebAMask-HQ (150 images)</Badge>
                  <Badge>1024x1024 Resolution</Badge>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-bold text-slate-900 mb-3 flex items-center gap-2">
                  <span className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-sm font-bold text-slate-600">2</span>
                  Models Tested
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {["Gemini 3 Pro Image", "Gemini 2.5 Flash", "GPT Image 1", "Emu 3.5", "Uni-MoE-2"].map((model) => (
                    <div key={model} className="bg-white border border-slate-200 px-3 py-2 rounded-lg text-sm font-medium text-slate-700 flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-indigo-500" />
                      {model}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-500 mt-3">Also compared with specialized models: SegFace, OneFormer, SAM 3.</p>
              </div>
            </div>

            <div className="space-y-6">
              <Card className="bg-slate-900 text-slate-300 border-slate-800 overflow-hidden relative">
                 <div className="absolute top-0 right-0 p-2 text-slate-600">
                    <Code2 size={20} />
                 </div>
                 <h4 className="text-sm font-medium text-slate-400 mb-4 border-b border-slate-800 pb-2">Prompt Template (CelebAMask-HQ)</h4>
                 <pre className="text-xs font-mono p-2 bg-black/30 rounded-lg border border-slate-800 leading-relaxed text-emerald-400 whitespace-pre-wrap break-words">
{`I want you to do semantic segmentation based on facial features. 
The label encodings are

\`\`\`
background : [0, 0, 0]
...
\`\`\`

For your convenience, I've also given you a color palette 
(the second image) for the label encodings.

Please draw a colorful mask, given the photo (the first image), 
the color palette and the label encodings.`}
                 </pre>
              </Card>

              <div className="bg-white p-2 rounded-xl border border-slate-200 shadow-sm">
                <Image 
                  src="/images/project/celeb/label-color-palette.png" 
                  alt="Color Palette" 
                  width={500} 
                  height={300}
                  className="rounded-lg w-full h-auto object-contain"
                />
                <p className="text-xs text-center text-slate-500 mt-2">Standard color encodings for CelebAMask-HQ</p>
              </div>
            </div>
          </div>
        </Section>

        {/* Results - Celeb */}
        <Section id="celeb">
          <SectionHeading icon={Palette}>CelebAMask-HQ Results</SectionHeading>
          
          <div className="prose prose-slate max-w-none mb-8 font-serif">
            <p>
              <strong>Gemini 3 Pro Image</strong> is the only OMM that understands the task requirements and completes it with high quality. Others either fail to understand the task or lack precise control.
            </p>
          </div>

          <div className="space-y-8">
            <figure>
              <Image 
                src="/images/project/celeb/model-comparison-celeb.png" 
                alt="Visual Comparison on CelebAMask-HQ" 
                width={1200} 
                height={600}
                className="rounded-xl shadow-lg border border-slate-200 w-full"
              />
              <figcaption className="text-center text-sm text-slate-500 mt-3">
                Visual comparison of different OMMs on CelebAMask-HQ face parsing.
              </figcaption>
            </figure>

            <div className="grid md:grid-cols-2 gap-6">
              <Card className="flex flex-col h-full">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="font-bold text-emerald-700 flex items-center gap-2">
                    <CheckCircle2 size={18} /> Best Result
                  </h4>
                  <Badge variant="success">F1: 0.708</Badge>
                </div>
                <Image 
                  src="/images/project/celeb/best-f1.png" 
                  alt="Best Result" 
                  width={600} 
                  height={400}
                  className="rounded-lg w-full"
                />
                <p className="text-xs text-slate-500 mt-2 text-center mt-auto">Gemini 3 Pro Best Prediction</p>
              </Card>

              <Card className="flex flex-col h-full">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="font-bold text-rose-700 flex items-center gap-2">
                    <AlertTriangle size={18} /> Worst Result
                  </h4>
                  <Badge variant="danger">F1: 0.081</Badge>
                </div>
                <Image 
                  src="/images/project/celeb/worst-f1.png" 
                  alt="Worst Result" 
                  width={600} 
                  height={400}
                  className="rounded-lg w-full"
                />
                <p className="text-xs text-slate-500 mt-2 text-center mt-auto">Gemini 3 Pro Worst Prediction</p>
              </Card>
            </div>

            {/* Charts & Graphs */}
            <div className="grid md:grid-cols-2 gap-6">
               <div className="space-y-2">
                  <h4 className="font-bold text-slate-900 text-center">Quantitative Results (F1)</h4>
                  <Image 
                    src="/images/project/celeb/quantatitive-results-f1.png" 
                    alt="Quantitative Results" 
                    width={800} 
                    height={600}
                    className="rounded-xl shadow-sm border border-slate-200 w-full bg-white p-2"
                  />
               </div>
               <div className="space-y-2">
                  <h4 className="font-bold text-slate-900 text-center">Data Contamination Check</h4>
                  <div className="bg-emerald-50 rounded-xl p-6 border border-emerald-100 h-full flex flex-col justify-center">
                    <p className="text-emerald-900 font-serif leading-relaxed">
                      We <strong>shuffled the color encodings</strong> to test for memorization. Surprisingly, performance <strong className="bg-emerald-200 px-1 rounded">increased by ~10%</strong>.
                    </p>
                    <div className="mt-4 pt-4 border-t border-emerald-200/50">
                      <p className="text-sm text-emerald-800 font-medium">Conclusion:</p>
                      <p className="text-sm text-emerald-700">The model truly understands the task and is not just retrieving memorized masks.</p>
                    </div>
                  </div>
               </div>
            </div>
          </div>
        </Section>

        {/* Results - COCO */}
        <Section id="coco">
          <SectionHeading icon={ImageIcon}>COCO Results</SectionHeading>
          
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-8 flex items-center gap-3">
             <AlertTriangle className="text-amber-600 shrink-0" />
             <p className="text-sm text-amber-800">
               COCO is significantly more challenging with 144 classes. Most models failed to generate valid masks.
             </p>
          </div>

          <figure className="mb-8">
            <Image 
              src="/images/project/coco/model-comparison.png" 
              alt="COCO Comparison" 
              width={1200} 
              height={600}
              className="rounded-xl shadow-lg border border-slate-200 w-full"
            />
            <figcaption className="text-center text-sm text-slate-500 mt-3">
              OneFormer (Specialized) vs Gemini 3 Pro vs Gemini 2.5 Flash on COCO.
            </figcaption>
          </figure>

          <div className="grid md:grid-cols-2 gap-6">
             <Card>
                <div className="text-center mb-2">
                   <h4 className="font-bold text-slate-900">Best Prediction (F1: 0.269)</h4>
                </div>
                <Image 
                  src="/images/project/coco/geminipro-best-coco.png" 
                  alt="Best COCO" 
                  width={600} 
                  height={400}
                  className="rounded-lg w-full"
                />
             </Card>
             <Card>
                <div className="text-center mb-2">
                   <h4 className="font-bold text-slate-900">Worst Prediction (F1: 0.0)</h4>
                </div>
                <Image 
                  src="/images/project/coco/geminipro-worst-coco.png" 
                  alt="Worst COCO" 
                  width={600} 
                  height={400}
                  className="rounded-lg w-full"
                />
             </Card>
          </div>
        </Section>

        {/* Discussion */}
        <Section id="discussion">
          <SectionHeading icon={FileText}>Discussion</SectionHeading>
          
          <div className="grid sm:grid-cols-2 gap-6">
            {[
              { icon: "📊", title: "Datasets", text: "PixelArena can be easily extended to other segmentation datasets." },
              { icon: "🔄", title: "Data Refinement", text: "OMM results are good enough to serve as annotation drafts for new datasets." },
              { icon: "✍️", title: "Better Prompts", text: "Under-specification in prompts (e.g., eyeball vs periorbital) affects results." },
              { icon: "📐", title: "Metric Design", text: "Score discrepancies don't always reflect visual similarity. Better metrics needed." }
            ].map((item, i) => (
              <Card key={i} className="bg-slate-50 border-none shadow-none hover:bg-white hover:shadow-md transition-all">
                <div className="text-3xl mb-3">{item.icon}</div>
                <h3 className="font-bold text-slate-900 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{item.text}</p>
              </Card>
            ))}
          </div>

          <div className="mt-12 bg-gradient-to-br from-indigo-50 to-white rounded-2xl p-8 border border-indigo-100 shadow-sm relative overflow-hidden">
             <div className="absolute top-0 right-0 -mt-10 -mr-10 w-32 h-32 bg-indigo-500 rounded-full blur-3xl opacity-10"></div>
             <div className="relative z-10">
                <h3 className="text-2xl font-bold mb-4 text-slate-900">Conclusion</h3>
                <p className="text-slate-700 leading-relaxed font-serif text-lg">
                  We present <strong>PixelArena</strong>, proving that Gemini 3 Pro Image represents a major breakthrough in pixel-precision visual intelligence. Our findings on zero-shot capabilities, failure modes, and data contamination provide a foundation for future research in OMMs.
                </p>
             </div>
          </div>

          {/* Citation - Commented out
          <div className="mt-12">
            <h3 className="font-bold text-slate-900 mb-4">Citation</h3>
            <pre className="bg-slate-100 text-slate-700 p-4 rounded-xl text-sm font-mono overflow-x-auto border border-slate-200">
{`@article{pixelarena2026,
  title={PixelArena: A Benchmark for Pixel-Precision Visual Intelligence},
  author={Anonymous},
  journal={IJCAI 2026 Submission},
  year={2026}
}`}
            </pre>
          </div>
          */}
        </Section>

      </div>

      <footer className="bg-white border-t border-slate-200 py-12">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-500">
          <p className="mb-2 font-semibold text-slate-900">PixelArena</p>
          <p className="text-sm">© 2026</p>
        </div>
      </footer>
    </div>
  );
}
