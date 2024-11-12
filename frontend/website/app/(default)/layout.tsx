"use client";

import { useEffect } from "react";
import { analytics } from "@/common/firebaseConfig";
import AOS from "aos";
import "aos/dist/aos.css";

import Footer from "@/components/ui/footer";

export default function DefaultLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    if (analytics) {
      console.log('Firebase analytics initialized globally');
    } else {
      console.warn('Firebase analytics is not initialized');
    }
  }, []);

  useEffect(() => {
    AOS.init({
      once: true,
      disable: "phone",
      duration: 600,
      easing: "ease-out-sine",
    });
  });

  return (
    <>
      <main className="relative flex grow flex-col">{children}</main>

      <Footer />
    </>
  );
}
