"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Features } from "./features";
import { ChatWithDocs } from "./chat-with-docs";

import { NavBar } from "./NavBar";
import { Footer } from "./Footer";

export function HomeV3() {
  return (
    <div className="flex flex-col min-h-screen">
      <NavBar />
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
              <div className="flex flex-col justify-center space-y-4">
                <div className="space-y-2">
                  <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
                    Building Planetary Omniscience
                  </h1>
                  <p className="max-w-[600px] text-muted-foreground md:text-xl">
                    Constellation is a pioneering startup building the AI
                    toolkit to answer the hardest planetary scale questions
                  </p>
                </div>
                <div className="flex flex-col gap-2 sm:flex-row">
                  <Link
                    href="/pipeline-builder"
                    className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
                  >
                    Get Started
                  </Link>
                  <Link
                    href="#features"
                    className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-8 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
                    prefetch={false}
                  >
                    Learn More
                  </Link>
                </div>
              </div>
              <div className="flex justify-center">
                <Image
                  src="/sun-light.svg"
                  width={600}
                  height={600}
                  alt="Earth visualization"
                  priority
                  className="w-full max-w-[600px] h-auto aspect-square overflow-hidden rounded-xl object-cover object-center"
                />
              </div>
            </div>
          </div>
        </section>

        <Features />

        <section className="w-full py-12 md:py-24 lg:py-32 bg-muted">
          <div className="container mx-auto px-4 md:px-6">
            <ChatWithDocs />
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container mx-auto px-4 md:px-6">
            <Footer />
          </div>
        </section>
      </main>
    </div>
  );
}
