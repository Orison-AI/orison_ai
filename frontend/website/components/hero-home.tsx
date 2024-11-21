"use client";

import { trackPageVisit } from "@/utils/trackers";
import { useEffect } from "react";

export default function HeroHome() {
  useEffect(() => {
    // Define an async function to handle the page visit tracking
    const trackPage = async () => {
      try {
        await trackPageVisit('Landing page visit');
      } catch (error) {
        console.error('Error tracking page visit:', error);
      }
    };

    trackPage();
  }, []);

  return (
    <section>
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        {/* Hero content */}
        <div className="py-12 md:py-20">
          {/* Section header */}
          <div className="pb-12 text-center md:pb-1">
            <h1
              className="animate-[gradient_6s_linear_infinite] bg-[linear-gradient(to_right,theme(colors.gray.200),theme(colors.indigo.200),theme(colors.gray.50),theme(colors.indigo.300),theme(colors.gray.200))] bg-[length:200%_auto] bg-clip-text pb-5 font-nacelle text-4xl font-semibold text-transparent md:text-5xl"
              data-aos="fade-up"
            >
              Orison AI
            </h1>
            <div className="mx-auto max-w-6xl"> {/* Control width using this xl */}
              <p
                className="mb-8 text-xl text-indigo-200/65"
                data-aos="fade-up"
                data-aos-delay={200}
              >
                Hybrid-AI agent for EB1, O-1, and Eb2 cases <br />
                Information intelligence for building your visa story and analytics to find your eligibility <br />
                Time is of essence in law so why use it on mundane tasks? <br />
                Take your heap of documents to review ready case file in minutes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
