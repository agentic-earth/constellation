import React from "react";
import Link from "next/link";
import Image from "next/image";

export default function Header() {
  return (
    <header className="px-4 lg:px-6 h-20 flex items-center">
      <Link href="#" className="flex items-center justify-center">
        <Image
          src="/sun-light.svg"
          width={60}
          height={60}
          alt="Geo AI Logo"
          className="h-12 w-12"
          draggable={false}
        />
        <span className="sr-only">Geo AI</span>
      </Link>
      <nav className="ml-auto flex gap-4 sm:gap-6">
        <Link
          href="#"
          className="text-sm font-medium hover:underline underline-offset-4"
        >
          Models
        </Link>
        <Link
          href="#"
          className="text-sm font-medium hover:underline underline-offset-4"
        >
          Research
        </Link>
        <Link
          href="#"
          className="text-sm font-medium hover:underline underline-offset-4"
        >
          Contact
        </Link>
      </nav>
    </header>
  );
}
