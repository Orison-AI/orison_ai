"use client";

import { handleButtonClick } from "@/utils/trackers";
import Logo from "./logo";

export default function Header() {
  const handleLoginClick = async () => {
    try {
      await handleButtonClick("login");
      // window.location.href = "https://www.app.orison.ai";
      window.open("https://www.app.orison.ai", "_blank");
    } catch (error) {
      console.error("Failed to log button click for login:", error);
      window.open("https://www.app.orison.ai", "_blank");
    }
  };

  const handleUserStudyClick = async () => {
    try {
      await handleButtonClick("user_study");
      window.open(
        "https://docs.google.com/forms/d/e/1FAIpQLSe0Y6ji6P3vOPC2etx-0NnxLFIRXbVv_QgxOZCKWC3-oLPThg/viewform?usp=sf_link",
        "_blank"
      );
    } catch (error) {
      console.error("Failed to log button click for User Study:", error);
      window.open(
        "https://docs.google.com/forms/d/e/1FAIpQLSe0Y6ji6P3vOPC2etx-0NnxLFIRXbVv_QgxOZCKWC3-oLPThg/viewform?usp=sf_link",
        "_blank"
      );
    }
  };

  const handleSampleContent = async () => {
    try {
      await handleButtonClick("sample_content");
      window.open("https://www.app.orison.ai", "_blank");
    } catch (error) {
      console.error("Failed to log button click for Sample Content:", error);
      window.open("https://www.app.orison.ai", "_blank");
    }
  };

  const handleUserGuideClick = async () => {
    try {
      await handleButtonClick("user_guide");
      window.open(
        "https://docs.google.com/presentation/d/1c3chlMKTA1YztjSGzH8p0bovqKoC2p5x/edit#slide=id.g315e2679ae5_0_0",
        "_blank"
      );
    } catch (error) {
      console.error("Failed to log button click for User Guide:", error);
      window.open(
        "https://docs.google.com/presentation/d/1c3chlMKTA1YztjSGzH8p0bovqKoC2p5x/edit#slide=id.g315e2679ae5_0_0",
        "_blank"
      );
    }
  };

  return (
    <header className="z-30 mt-2 w-full md:mt-5">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="relative flex h-20 items-center justify-between gap-4 rounded-2xl bg-gray-900/90 px-6 before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_right,theme(colors.gray.800),theme(colors.gray.700),theme(colors.gray.800))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] after:absolute after:inset-0 after:-z-10 after:backdrop-blur-sm">
          {/* Site branding */}
          <div className="flex flex-1 items-center">
            <Logo />
          </div>

          {/* Desktop sign in links */}
          <ul className="flex flex-1 items-center justify-end gap-4">
            <li>
              <button
                onClick={handleLoginClick}
                className="relative flex items-center justify-center w-48 bg-gradient-to-b from-gray-800 to-gray-800/60 bg-[length:100%_100%] bg-[bottom] py-2 px-4 text-lg text-gray-300 font-semibold before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_right,theme(colors.gray.800),theme(colors.gray.700),theme(colors.gray.800))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] hover:bg-[length:100%_150%]"
              >
                Log In
              </button>
            </li>
            <li>
              <button
                onClick={handleUserStudyClick}
                className="relative flex items-center justify-center w-48 bg-gradient-to-b from-gray-800 to-gray-800/60 bg-[length:100%_100%] bg-[bottom] py-2 px-4 text-lg text-gray-300 font-semibold before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_right,theme(colors.gray.800),theme(colors.gray.700),theme(colors.gray.800))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] hover:bg-[length:100%_150%]"
              >
                Feedback Form
              </button>
            </li>
            <li>
              <button
                onClick={handleUserGuideClick}
                className="relative flex items-center justify-center w-48 bg-gradient-to-b from-gray-800 to-gray-800/60 bg-[length:100%_100%] bg-[bottom] py-2 px-4 text-lg text-gray-300 font-semibold before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_right,theme(colors.gray.800),theme(colors.gray.700),theme(colors.gray.800))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] hover:bg-[length:100%_150%]"
              >
                User Guide
              </button>
            </li>
            <li>
              <button
                onClick={handleSampleContent}
                className="relative flex items-center justify-center w-48 bg-gradient-to-b from-gray-800 to-gray-800/60 bg-[length:100%_100%] bg-[bottom] py-2 px-4 text-lg text-gray-300 font-semibold before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_right,theme(colors.gray.800),theme(colors.gray.700),theme(colors.gray.800))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] hover:bg-[length:100%_150%]"
              >
                Sample Doc
              </button>
            </li>
          </ul>

        </div>
      </div>
    </header>
  );
}
