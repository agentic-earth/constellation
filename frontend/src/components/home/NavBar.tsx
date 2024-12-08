import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import {
  ChevronDown,
  Rocket,
  LogIn,
  Library,
  PlusSquare,
  CloudRain,
  Settings,
  Info,
  Users,
  Phone,
  HelpCircle,
} from "lucide-react";

const navItems = [
  {
    title: "About",
    links: [
      { title: "Our Mission", href: "#mission", icon: Info },
      { title: "Team", href: "#team", icon: Users },
      {
        title: "How Composer Works",
        href: "/how-composer-works",
        icon: HelpCircle,
      },
    ],
  },
  {
    title: "Contact",
    links: [{ title: "Contact Us", href: "/contact", icon: Phone }],
  },
];

export function NavBar() {
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleToggleDropdown = (title: string) => {
    setOpenDropdown(openDropdown === title ? null : title);
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setOpenDropdown(null);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50 px-4 lg:px-6 h-20 flex items-center justify-between bg-background shadow-sm">
        <div className="flex-1 flex justify-start">
          <Link
            href="/"
            className="flex items-center justify-center ml-4"
            prefetch={false}
          >
            <div className="w-48 h-14 relative">
              {" "}
              {/* Increased size by 50% */}
              <Image
                src="/constellation.svg"
                alt="Constellation Labs Logo"
                layout="fill"
                objectFit="contain"
                className="h-full w-auto"
                draggable={false}
              />
            </div>
          </Link>
        </div>
        <></>
        <div className="flex items-center space-x-4 flex-1 justify-end">
          <Link href="/pipeline-builder" passHref>
            <Button
              size="sm"
              className="rounded-full bg-white text-black hover:bg-gray-100 flex items-center"
            >
              <Rocket className="h-4 w-4 mr-2" />
              Get Started
            </Button>
          </Link>
        </div>
      </header>
      <div className="h-20"></div>{" "}
      {/* This div adds spacing equal to the new NavBar height */}
    </>
  );
}
