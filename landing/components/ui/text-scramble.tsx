"use client"

import { useState, useCallback, useRef, useEffect } from "react"

const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

interface TextScrambleProps {
  text: string
  className?: string
}

export function TextScramble({ text, className = "" }: TextScrambleProps) {
  const [displayText, setDisplayText] = useState(text)
  const [isHovering, setIsHovering] = useState(false)
  const [isScrambling, setIsScrambling] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const frameRef = useRef(0)

  const scramble = useCallback(() => {
    setIsScrambling(true)
    frameRef.current = 0
    const duration = text.length * 3

    if (intervalRef.current) clearInterval(intervalRef.current)

    intervalRef.current = setInterval(() => {
      frameRef.current++

      const progress = frameRef.current / duration
      const revealedLength = Math.floor(progress * text.length)

      const newText = text
        .split("")
        .map((char, i) => {
          // Treat spaces and newlines as separators
          if (char === " " || char === "\n") return char

          // Determine the position and length of the current word so
          // each word can reveal from its start concurrently.
          let start = i
          while (start > 0 && text[start - 1] !== " " && text[start - 1] !== "\n") start--
          let end = i
          while (end + 1 < text.length && text[end + 1] !== " " && text[end + 1] !== "\n") end++

          const wordLen = end - start + 1
          const posInWord = i - start
          const revealedForWord = Math.floor(progress * wordLen)

          if (posInWord < revealedForWord) return text[i]

          const target = text[i]
          const isAsciiLetter = /[A-Za-z]/.test(target)

          if (isAsciiLetter) {
            const pool = target === target.toLowerCase() ? CHARS.toLowerCase() : CHARS
            return pool[Math.floor(Math.random() * pool.length)]
          }

          return CHARS[Math.floor(Math.random() * CHARS.length)]
        })
        .join("")

      setDisplayText(newText)

      if (frameRef.current >= duration) {
        if (intervalRef.current) clearInterval(intervalRef.current)
        setDisplayText(text)
        setIsScrambling(false)
      }
    }, 30)
  }, [text])

  const handleMouseEnter = () => {
    setIsHovering(true)
    scramble()
  }

  const handleMouseLeave = () => {
    setIsHovering(false)
  }

  // Auto-start scramble on mount (or when `text` changes)
  useEffect(() => {
    scramble()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scramble])

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [])

  return (
    <div
      className={`group relative flex flex-col items-center justify-center cursor-pointer select-none ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <span className="relative font-mono tracking-tight font-light text-center">
        {
          // Tokenize displayText into words, spaces, and newlines while preserving indices
          (() => {
            const tokens: Array<{
              type: "word" | "space" | "newline"
              chars: string[]
              indices: number[]
            }> = []

            const s = displayText
            let i = 0
            while (i < s.length) {
              const ch = s[i]
              if (ch === "\n") {
                tokens.push({ type: "newline", chars: [], indices: [] })
                i++
                continue
              }

              if (ch === " ") {
                tokens.push({ type: "space", chars: [ch], indices: [i] })
                i++
                continue
              }

              // word
              const chars: string[] = []
              const indices: number[] = []
              while (i < s.length && s[i] !== " " && s[i] !== "\n") {
                chars.push(s[i])
                indices.push(i)
                i++
              }
              tokens.push({ type: "word", chars, indices })
            }

            return tokens.map((token, ti) => {
              if (token.type === "newline") return <br key={`nl-${ti}`} />

              if (token.type === "space") {
                // Render a single breakable space between words
                return (
                  <span key={`sp-${token.indices[0]}`} className="inline-block">
                    {"\u00A0"}
                  </span>
                )
              }

              // word: prevent internal wrapping so the word stays intact
              return (
                <span key={`w-${ti}`} className="inline-block whitespace-nowrap">
                  {token.chars.map((char, idx) => {
                    const origIndex = token.indices[idx]
                    const displayChar = char === " " ? "\u00A0" : char
                    return (
                      <span
                        key={origIndex}
                        className={`inline-block transition-all duration-150 ${isScrambling && char !== text[origIndex] ? "text-green-400 scale-110" : "text-white"}`}
                        style={{ transitionDelay: `${origIndex * 10}ms` }}
                      >
                        {displayChar}
                      </span>
                    )
                  })}
                </span>
              )
            })
          })()
        }
      </span>

      {/* Animated underline */}
      <span className="relative h-px w-full mt-2 overflow-hidden">
        <span
          className={`absolute inset-0 bg-white transition-transform duration-500 ease-out origin-left ${isHovering ? "scale-x-100" : "scale-x-0"
            }`}
        />
        <span className="absolute inset-0 bg-neutral-800" />
      </span>

      {/* Subtle glow on hover */}
      <span
        className={`absolute -inset-4 rounded-lg bg-green-500/5 transition-opacity duration-300 -z-10 ${isHovering ? "opacity-100" : "opacity-0"
          }`}
      />
    </div>
  )
}
