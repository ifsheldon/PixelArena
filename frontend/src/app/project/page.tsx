import Image from "next/image";

export default function ProjectPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900 font-sans py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-12">
        
        {/* Header Section */}
        <header className="text-center space-y-6">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-gray-900">
            PixelArena: A benchmark for Pixel-Precision Visual Intelligence
          </h1>
          
          <div className="space-y-2">
            <div className="text-xl text-gray-700">
              <span>Feng Liang*</span>, <span>Sizhe Cheng*</span>, <span>Chenqi Yi</span>
            </div>
            <div className="text-lg text-gray-600">
              Nanyang Technological University
            </div>
          </div>

          <div className="flex justify-center gap-4 pt-4">
            {/* Paper Button */}
            <a 
              href="https://arxiv.org/abs/2512.16303" 
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-6 py-2 border border-transparent text-base font-medium rounded-full shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Paper
            </a>

            {/* Code Button */}
            <a 
              href="https://github.com/ifsheldon/pixel-arena-data-processing" 
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-6 py-2 border border-gray-300 text-base font-medium rounded-full shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Code
            </a>

            {/* Gallery Button */}
            <a 
              href="/" 
              className="inline-flex items-center px-6 py-2 border border-gray-300 text-base font-medium rounded-full shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Gallery
            </a>
          </div>
        </header>

        {/* Abstract */}
        <section className="bg-gray-50 rounded-2xl p-8 shadow-sm">
          <h2 className="text-2xl font-semibold mb-4 text-gray-900">Abstract</h2>
          <p className="text-gray-700 leading-relaxed text-lg text-justify">
            Multi-modal large language models that have image output are emerging. Many image generation benchmarks focus on aesthetics instead of fine-grained generation capabilities. In <strong>PixelArena</strong>, we propose using semantic segmentation tasks to objectively examine their fine-grained generative intelligence with pixel precision. 
            We find the latest Gemini 3 Pro Image has emergent image generation capabilities that generate semantic masks with high fidelity under zero-shot settings, showcasing visual intelligence unseen before and true generalization in new image generation tasks. 
            We further investigate its results, compare them qualitatively and quantitatively with those of other models, and present failure cases. The findings not only signal exciting progress in the field but also provide insights into future research related to multimodality, reasoning, interpretability and benchmarking.
          </p>
        </section>

        {/* Introduction / Overview */}
        <section className="space-y-6">
          <h2 className="text-3xl font-bold text-gray-900 border-b pb-2">Introduction</h2>
          <p className="text-lg text-gray-700 leading-relaxed">
            Since the release of GPT-4o, Multi-modal Large Language Models (MLLMs) have gained significant attention. While much focus has been placed on image quality and aesthetics, few studies have quantitatively examined the precision and generalizability of the image generation capabilities of these models.
          </p>
          <p className="text-lg text-gray-700 leading-relaxed">
            In PixelArena, we propose using pixel-level tasks (e.g., face parsing and general semantic segmentation) to examine MLLMs' fine-grained control capability and their generalizability in image generation, which we term <strong>Pixel-Precision Visual Intelligence (PPVI)</strong>.
          </p>
        </section>

        {/* Methods */}
        <section className="space-y-6">
          <h2 className="text-3xl font-bold text-gray-900 border-b pb-2">Methodology</h2>
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div className="space-y-4">
              <p className="text-lg text-gray-700 leading-relaxed">
                We task MLLMs to perform semantic segmentation on CelebAMask-HQ and COCO datasets. 
                Instead of training specialized heads, we provide the models with a color palette and prompt them to generate the segmentation mask directly as an image. This zero-shot approach tests the model's true understanding and instruction following capabilities.
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <div className="aspect-w-16 aspect-h-9 relative">
                <Image 
                  src="/images/project/celeb/label-color-palette.png" 
                  alt="Color Palette for Segmentation" 
                  width={500} 
                  height={300}
                  className="rounded-lg object-contain w-full h-auto"
                />
                <p className="text-sm text-gray-500 mt-2 text-center">Palette of the standard color encodings from CelebAMask-HQ</p>
              </div>
            </div>
          </div>
        </section>

        {/* Results - Celeb */}
        <section className="space-y-8">
          <h2 className="text-3xl font-bold text-gray-900 border-b pb-2">Results on CelebAMask-HQ</h2>
          
          <div className="space-y-4">
            <p className="text-lg text-gray-700 leading-relaxed">
              We compared several state-of-the-art MLLMs including Gemini 3 Pro, Gemini 2.5, GPT Image, and specialized models like SegFace and SAM 3.
            </p>
            
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 my-8">
              <Image 
                src="/images/project/celeb/model-comparison-celeb.png" 
                alt="Visual Comparison on CelebAMask-HQ" 
                width={1200} 
                height={600}
                className="rounded-lg w-full h-auto"
              />
              <p className="text-sm text-gray-500 mt-3 text-center">Qualitative comparison of face parsing results across different models.</p>
            </div>

            <p className="text-lg text-gray-700 leading-relaxed">
              Quantitative results show that Gemini 3 Pro achieves remarkable performance, often rivaling or surpassing specialized models in certain aspects, despite being a general-purpose MLLM operating in a zero-shot setting.
            </p>

            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 my-8 flex justify-center">
              <div className="w-full max-w-2xl">
                <Image 
                  src="/images/project/celeb/quantatitive-results-f1.png" 
                  alt="Quantitative Results F1 Score" 
                  width={800} 
                  height={600}
                  className="rounded-lg w-full h-auto"
                />
                <p className="text-sm text-gray-500 mt-3 text-center">F1 Scores on CelebAMask-HQ dataset.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Results - COCO */}
        <section className="space-y-8">
          <h2 className="text-3xl font-bold text-gray-900 border-b pb-2">Results on COCO</h2>
          
          <div className="space-y-4">
            <p className="text-lg text-gray-700 leading-relaxed">
              We extended our benchmark to the more challenging COCO dataset to test generalization. Gemini 3 Pro continues to demonstrate strong performance.
            </p>
            
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 my-8">
              <Image 
                src="/images/project/coco/model-comparison.png" 
                alt="Visual Comparison on COCO" 
                width={1200} 
                height={600}
                className="rounded-lg w-full h-auto"
              />
              <p className="text-sm text-gray-500 mt-3 text-center">Visual comparison of semantic segmentation on COCO dataset.</p>
            </div>

            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 my-8">
              <Image 
                src="/images/project/coco/geminipro-best-coco.png" 
                alt="Best Results on COCO" 
                width={1200} 
                height={600}
                className="rounded-lg w-full h-auto"
              />
              <p className="text-sm text-gray-500 mt-3 text-center">Selected best results from Gemini 3 Pro on COCO.</p>
            </div>
          </div>
        </section>

        {/* Citation */}
        <section className="bg-gray-50 rounded-2xl p-8 shadow-sm">
          <h2 className="text-xl font-bold mb-4 text-gray-900">Citation</h2>
          <pre className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono">
{`@article{pixelarena2026,
  title={PixelArena: A benchmark for Pixel-Precision Visual Intelligence},
  author={Liang, Feng and Cheng, Sizhe and Yi, Chenqi},
  journal={arXiv preprint},
  year={2026}
}`}
          </pre>
        </section>

      </div>
    </div>
  );
}

