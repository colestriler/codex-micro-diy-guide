"use client";

import { useEffect, useState } from "react";

export const sections = [
  { id: "before-you-start", title: "Before you start" },
  { id: "parts", title: "Parts checklist" },
  { id: "printing", title: "3D printing" },
  { id: "assembly", title: "Assembly" },
  { id: "software", title: "Firmware & colors" },
  { id: "checks", title: "Final checks" },
  { id: "files", title: "Downloads" },
];

export default function TableOfContents() {
  const [active, setActive] = useState(sections[0].id);

  useEffect(() => {
    let frame = 0;
    const update = () => {
      frame = 0;
      let current = sections[0].id;
      for (const section of sections) {
        const heading = document.getElementById(section.id);
        if (heading && heading.getBoundingClientRect().top <= 150) current = section.id;
      }
      setActive(current);
    };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(update); };
    update();
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("scroll", schedule);
      window.removeEventListener("resize", schedule);
    };
  }, []);

  return <aside className="guide-sidebar"><nav aria-label="Table of contents"><p className="toc-label">Build guide</p><ol>{sections.map((section, index) => <li key={section.id}><a href={`#${section.id}`} aria-current={active === section.id ? "location" : undefined}><span aria-hidden="true">{String(index + 1).padStart(2, "0")}</span>{section.title}</a></li>)}</ol><a className="toc-top" href="#top">Back to top ↑</a></nav></aside>;
}
