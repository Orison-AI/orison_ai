"use client";

import { handleButtonClick } from "@/utils/trackers";
import Logo from "./logo";

export default function Header() {
  const handleLoginClick = async () => {
    try {
      await handleButtonClick("Header login button clicked");
      window.location.href = "https://www.app.orison.ai"; // Navigate after logging
    } catch (error) {
      console.error("Failed to log button click:", error);
      window.location.href = "https://www.app.orison.ai"; // Ensure navigation even on error
    }
  };

  return (
    <header className="z-30 mt-2 w-full md:mt-5">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="relative flex h-20 items-center justify-between gap-3 rounded-2xl bg-gray-900/90 px-6 before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_right,theme(colors.gray.800),theme(colors.gray.700),theme(colors.gray.800))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] after:absolute after:inset-0 after:-z-10 after:backdrop-blur-sm">
          {/* Site branding */}
          <div className="flex flex-1 items-center">
            <Logo />
          </div>

          {/* Desktop sign in links */}
          <ul className="flex flex-1 items-center justify-end gap-3">
            <li>
              <button
                onClick={handleLoginClick} // Call handleLoginClick on button click
                className="relative flex items-center justify-center bg-gradient-to-b from-gray-800 to-gray-800/60 bg-[length:100%_100%] bg-[bottom] py-[10px] px-[16px] text-lg text-gray-300 font-semibold before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_right,theme(colors.gray.800),theme(colors.gray.700),theme(colors.gray.800))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] hover:bg-[length:100%_150%]"
              >
                Log In
              </button>
            </li>
          </ul>
        </div>
      </div>
    </header>
  );
}
