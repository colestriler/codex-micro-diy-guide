"use client";

import { useEffect, useState } from "react";
import catalog from "@/data/parts.json";

type Part = (typeof catalog)[number];
const storageKey = "codex-micro:parts:v1";
const rowNumbers = new Map(catalog.map((part, index) => [part.id, index + 1]));

function decodeChecks(value: string | null): Set<string> {
  try {
    const data: unknown = JSON.parse(value ?? "[]");
    return new Set(Array.isArray(data) ? data.filter((id): id is string => typeof id === "string" && rowNumbers.has(id)) : []);
  } catch {
    return new Set();
  }
}

export default function PartsTable({ parts, onSelect }: { parts: Part[]; onSelect: (part: Part) => void }) {
  const [checked, setChecked] = useState<Set<string>>(() => new Set());
  const [storage, setStorage] = useState<"loading" | "saved" | "unavailable">("loading");
  const groups = [
    { id: "print-parts", title: "Print", description: "Make these on your 3D printer.", parts: parts.filter(part => part.category === "Printed") },
    { id: "buy-parts", title: "Buy", description: "Electronics, hardware, materials, and donor options.", parts: parts.filter(part => part.category !== "Printed") },
  ];

  useEffect(() => {
    try {
      setChecked(decodeChecks(localStorage.getItem(storageKey)));
      setStorage("saved");
    } catch {
      setStorage("unavailable");
    }
    const sync = (event: StorageEvent) => {
      if (event.key === storageKey || event.key === null) {
        setChecked(decodeChecks(event.newValue));
      }
    };
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);

  function toggle(id: string, haveIt: boolean) {
    let next = new Set(checked);
    try {
      // Merge with the latest saved selection, including changes from other tabs.
      if (storage !== "unavailable") next = decodeChecks(localStorage.getItem(storageKey));
    } catch {
      // Keep the checklist usable for this visit when storage is blocked.
    }
    if (haveIt) next.add(id);
    else next.delete(id);
    setChecked(next);
    try {
      localStorage.setItem(storageKey, JSON.stringify([...next]));
      setStorage("saved");
    } catch {
      setStorage("unavailable");
    }
  }

  return (
    <>
      <div className="checklist-status" aria-live="polite">
        <span>{checked.size} {checked.size === 1 ? "item" : "items"} checked</span>
        <span>{storage === "loading" ? "Loading your checklist…" : storage === "saved" ? "Saved in this browser" : "Storage unavailable · checks last for this visit"}</span>
      </div>
      {groups.filter(group => group.parts.length > 0).map(group => <section className="parts-group" key={group.id} aria-labelledby={group.id}>
      <div className="parts-group-heading"><h3 id={group.id}>{group.title}<span>{group.parts.length} items</span></h3><p>{group.description}</p></div>
      <div className="parts-sheet-scroll" tabIndex={0} role="region" aria-label={`${group.title} checklist; scroll to see all columns`}>
        <table className="parts-sheet">
          <caption className="sr-only">{group.title} checklist. Check off parts you have. {group.id === "print-parts" ? "Click a part name for print files." : "Part names open supplier links in a new tab."}</caption>
          <thead><tr><th scope="col" className="sheet-number">#</th><th scope="col" className="sheet-check">Have</th><th scope="col">Part</th><th scope="col">{group.id === "print-parts" ? "Material" : "Type"}</th><th scope="col">Quantity</th><th scope="col">Get it</th></tr></thead>
          <tbody>{group.parts.map(part => (
            <tr key={part.id} data-checked={checked.has(part.id)}>
              <td className="sheet-number">{rowNumbers.get(part.id)}</td>
              <td className="sheet-check"><label className="sheet-check-target"><input type="checkbox" aria-label={`Have ${part.name}`} checked={checked.has(part.id)} disabled={storage === "loading"} onChange={event => toggle(part.id, event.target.checked)} /></label></td>
              <th scope="row">{part.category === "Printed" ? <button className="sheet-part" onClick={() => onSelect(part)}>{part.name}<span aria-hidden="true">↗</span></button> : <a className="sheet-part" href={part.links[0].url} target="_blank" rel="noopener noreferrer">{part.name}<span aria-hidden="true">↗</span></a>}</th>
              <td className="sheet-type">{part.category === "Printed" ? part.material : part.category}</td>
              <td className="sheet-quantity">{part.quantity}</td>
              <td className="sheet-action">{part.category === "Printed" ? <button onClick={() => onSelect(part)} aria-label={`Print files for ${part.name}`}>Print files ↓</button> : <a href={part.links[0].url} target="_blank" rel="noopener noreferrer" aria-label={`Buy ${part.name}`}>Buy ↗</a>}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
      </section>)}
    </>
  );
}
