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
      <div className="parts-sheet-scroll" tabIndex={0} role="region" aria-label="Parts checklist; scroll to see all columns">
        <table className="parts-sheet">
          <caption className="sr-only">Check off parts you have. Click a part name for details, files, and buying links.</caption>
          <thead><tr><th scope="col" className="sheet-number">#</th><th scope="col" className="sheet-check">Have</th><th scope="col">Part</th><th scope="col">Type</th><th scope="col">Quantity</th><th scope="col">Get it</th></tr></thead>
          <tbody>{parts.map(part => (
            <tr key={part.id} data-checked={checked.has(part.id)}>
              <td className="sheet-number">{rowNumbers.get(part.id)}</td>
              <td className="sheet-check"><label className="sheet-check-target"><input type="checkbox" aria-label={`Have ${part.name}`} checked={checked.has(part.id)} disabled={storage === "loading"} onChange={event => toggle(part.id, event.target.checked)} /></label></td>
              <th scope="row"><button className="sheet-part" onClick={() => onSelect(part)}>{part.name}<span aria-hidden="true">↗</span></button></th>
              <td className="sheet-type">{part.category === "Printed" ? "3D print" : part.category}</td>
              <td className="sheet-quantity">{part.quantity}</td>
              <td className="sheet-action">{part.category === "Printed" ? <button onClick={() => onSelect(part)} aria-label={`Print files for ${part.name}`}>Print files ↓</button> : <a href={part.links[0].url} target="_blank" rel="noopener noreferrer" aria-label={`Buy ${part.name}`}>Buy ↗</a>}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </>
  );
}
