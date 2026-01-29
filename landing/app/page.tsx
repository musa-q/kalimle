"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { TextScramble } from "@/components/ui/text-scramble"
import Link from "next/link"
import { ArrowRight, Check, ArrowDown } from "lucide-react"

const languages = [
  {
    name: "Kalimle",
    language: "Arabic",
    script: "كلمة",
    status: "available",
    description: "Master Arabic vocabulary through daily puzzles",
  },
  {
    name: "Sözle",
    language: "Turkish",
    script: "Söz",
    status: "available",
    description: "Discover Turkish words one puzzle at a time",
  },
  {
    name: "Coming Soon",
    language: "Spanish",
    script: "Palabra",
    status: "soon",
    description: "Expand your Spanish lexicon",
  },
  {
    name: "Coming Soon",
    language: "French",
    script: "Mot",
    status: "soon",
    description: "Enrich your French vocabulary",
  },
]

const features = [
  "One thoughtful puzzle daily",
  "Learn through pattern recognition",
  "Track your learning streak",
  "No ads, no distractions",
]

export default function Home() {
  const [selectedLanguage, setSelectedLanguage] = useState<string | null>(null)
  const [hoveredTile, setHoveredTile] = useState<number | null>(null)

  return (
    <main className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="flex min-h-screen flex-col items-center justify-center px-6 py-20">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-8">
            <TextScramble
              text={`Daily Language\nPuzzles`}
              className="text-5xl font-light tracking-tight sm:text-7xl lg:text-8xl"
            />
          </div>
          <p className="mx-auto mb-4 max-w-2xl text-balance text-lg leading-relaxed text-neutral-400 sm:text-xl">
            A growing family of word games designed to help you learn languages through focused, daily practice.
          </p>
          <p className="mx-auto max-w-xl text-pretty text-sm leading-relaxed text-neutral-500 sm:text-base">
            One puzzle. One language. Every day. Build vocabulary through pattern recognition and mindful repetition.
          </p>

          <div className="mt-12 flex flex-col items-center gap-6">
            <a href="#languages" className="group flex items-center gap-3 rounded-full bg-neutral-900/40 px-4 py-2 text-sm text-neutral-200 transition-transform duration-300 hover:scale-105">
              <span className="text-sm font-medium">Try out now</span>
              <ArrowDown className="h-5 w-5 animate-bounce text-green-400" />
            </a>

            <div className="w-full max-w-3xl">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Link href="/kalimle" className="flex items-center justify-between gap-4 rounded-lg border border-neutral-800 bg-neutral-950/50 px-6 py-5 transition hover:bg-neutral-900/60">
                  <div>
                    <div className="font-mono text-2xl text-yellow-400">كلمة</div>
                    <div className="text-lg font-medium">Kalimle</div>
                    <div className="text-sm text-neutral-400">Arabic — Play now</div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-green-400" />
                </Link>

                <Link href="/sozle" className="flex items-center justify-between gap-4 rounded-lg border border-neutral-800 bg-neutral-950/50 px-6 py-5 transition hover:bg-neutral-900/60">
                  <div>
                    <div className="font-mono text-2xl text-yellow-400">Söz</div>
                    <div className="text-lg font-medium">Sözle</div>
                    <div className="text-sm text-neutral-400">Turkish — Play now</div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-green-400" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section> 

      {/* How It Works Section */}
      <section className="border-t border-neutral-800 px-6 py-32">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-16 text-center font-mono text-3xl font-light tracking-tight sm:text-4xl">How It Works</h2>

          <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { step: "01", title: "Guess", desc: "Enter a word in your target language" },
              { step: "02", title: "Learn", desc: "Colored tiles reveal your progress" },
              { step: "03", title: "Refine", desc: "Use feedback to improve your next guess" },
              { step: "04", title: "Succeed", desc: "Solve the puzzle and build your streak" },
            ].map((item, i) => (
              <div
                key={i}
                className="group relative"
                onMouseEnter={() => setHoveredTile(i)}
                onMouseLeave={() => setHoveredTile(null)}
              >
                <div
                  className={`absolute -inset-2 rounded-lg bg-gradient-to-b from-green-500/5 to-yellow-500/5 opacity-0 blur transition-opacity duration-500 ${hoveredTile === i ? "opacity-100" : ""
                    }`}
                />
                <div className="relative space-y-4">
                  <div className="font-mono text-sm text-green-400">{item.step}</div>
                  <h3 className="text-xl font-light">{item.title}</h3>
                  <p className="text-pretty text-sm leading-relaxed text-neutral-400">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Visual Puzzle Example */}
          <div className="mt-20 flex justify-center">
            <div className="inline-flex gap-2">
              {[
                { letter: "ك", color: "bg-green-600" },
                { letter: "ت", color: "bg-yellow-600" },
                { letter: "ا", color: "bg-neutral-700" },
                { letter: "ب", color: "bg-green-600" },
              ].map((tile, i) => (
                <div
                  key={i}
                  className={`flex h-16 w-16 items-center justify-center rounded ${tile.color} font-mono text-2xl font-semibold text-white shadow-lg transition-transform duration-300 hover:-translate-y-1`}
                >
                  {tile.letter}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Why Different Section */}
      <section className="border-t border-neutral-800 px-6 py-32">
        <div className="mx-auto max-w-3xl">
          <h2 className="mb-16 text-center font-mono text-3xl font-light tracking-tight sm:text-4xl">
            Why This Matters
          </h2>

          <div className="space-y-8">
            {features.map((feature, i) => (
              <div
                key={i}
                className="group flex items-start gap-4 rounded-lg border border-neutral-800 bg-neutral-950/50 p-6 transition-colors duration-300 hover:border-neutral-700"
              >
                <div className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-green-600/20">
                  <Check className="h-3 w-3 text-green-400" />
                </div>
                <p className="text-pretty text-lg leading-relaxed text-neutral-300">{feature}</p>
              </div>
            ))}
          </div>

          <p className="mt-12 text-pretty text-center text-sm leading-relaxed text-neutral-500">
            Designed for learners who value quality over quantity. Each puzzle is carefully crafted to respect your time
            and attention.
          </p>
        </div>
      </section>

      {/* Language Selection Section */}
      <section id="languages" className="border-t border-neutral-800 px-6 py-32">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-6 text-center font-mono text-3xl font-light tracking-tight sm:text-4xl">
            Choose Your Language
          </h2>
          <p className="mb-16 text-balance text-center text-neutral-400">
            Start with Arabic or Turkish. More languages arriving soon.
          </p>

          <div className="grid gap-6 sm:grid-cols-2">
            {languages.map((lang, i) => (
              <button
                key={i}
                onClick={() => lang.status === "available" && setSelectedLanguage(lang.name)}
                disabled={lang.status === "soon"}
                className={`group relative overflow-hidden rounded-lg border p-8 text-left transition-all duration-300 ${lang.status === "available"
                  ? selectedLanguage === lang.name
                    ? "border-green-600 bg-green-600/5"
                    : "border-neutral-800 bg-neutral-950/50 hover:border-neutral-700"
                  : "cursor-not-allowed border-neutral-900 bg-neutral-950/30 opacity-50"
                  }`}
              >
                <div className="relative z-10">
                  <div className="mb-4 font-mono text-4xl text-yellow-400">{lang.script}</div>
                  <h3 className="mb-1 text-2xl font-light">{lang.name}</h3>
                  <p className="mb-3 text-sm text-neutral-400">{lang.language}</p>
                  <p className="text-pretty text-sm leading-relaxed text-neutral-500">{lang.description}</p>
                  {lang.status === "soon" && (
                    <div className="mt-4 inline-block rounded-full bg-neutral-800 px-3 py-1 text-xs text-neutral-400">
                      Coming Soon
                    </div>
                  )}
                </div>
                {lang.status === "available" && (
                  <div className="absolute right-4 top-4 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                    <ArrowRight className="h-5 w-5 text-green-400" />
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="border-t border-neutral-800 px-6 py-32">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-6 text-balance font-mono text-3xl font-light tracking-tight sm:text-4xl">
            Begin Your Practice
          </h2>
          <p className="mb-10 text-pretty text-lg leading-relaxed text-neutral-400">
            Join learners who choose focused, meaningful practice over endless scrolling.
          </p>

          <Button
            size="lg"
            className="group h-14 bg-green-600 px-8 text-base font-medium text-white hover:bg-green-700"
          >
            Start Playing Today
            <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
          </Button>

          <p className="mt-6 text-sm text-neutral-500">Free to play. No account required to start.</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-neutral-900 px-6 py-12">
        <div className="mx-auto max-w-5xl">
          <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
            <p className="font-mono text-sm text-neutral-600">© 2026 Daily Language Puzzles</p>
            <div className="flex gap-8 text-sm text-neutral-600">
              <a href="#" className="transition-colors duration-200 hover:text-neutral-400">
                About
              </a>
              <a href="#" className="transition-colors duration-200 hover:text-neutral-400">
                Privacy
              </a>
              <a href="#" className="transition-colors duration-200 hover:text-neutral-400">
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  )
}
