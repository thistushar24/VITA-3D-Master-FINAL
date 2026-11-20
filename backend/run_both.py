"""
run_both.py  -  ONE command for upper + lower jaw.

    python run_both.py                      your own photo (patient_photo.jpg)
    python run_both.py --patient Patient_1  a dataset photo (no clicking)

What it does, with progress printed at every step:
  1. loads a starter upper arch and a starter lower arch
  2. you click the upper teeth, then the lower teeth   (K skips a jaw)
  3. picks the BEST-matching arch for each jaw from your library (first run indexes
     the library and saves the result, later runs are instant)
  4. opens both jaws together on the photo to fine-tune and save

Options:  --limit N  arches to index per jaw this run (default 60; more = better match, slower)
          --no-search  skip step 3 and use the starter arches
"""
import argparse
import os

import dental_overlay as do
import find_best_arch as fb

TOTAL = 4


def step(n, text):
    print(f"\n[{n}/{TOTAL}] {text}", flush=True)


def pick_best(jaw, start_case, clicks, args):
    library = os.path.dirname(start_case)
    cases = fb.list_cases(library)
    if not cases:
        print(f"   {jaw}: no arches found in {library} - keeping the starter arch", flush=True)
        return start_case
    cache = fb.load_cache(fb.CACHE_FILE)
    print(f"   {jaw}: {len(cases)} arches in the library", flush=True)
    cache = fb.build_cache(cases, cache, args.limit, args.workers)
    with open(fb.CACHE_FILE, "w") as fh:
        fb.json.dump(cache, fh)
    rows = fb.rank({c: cache[c] for c in cases if c in cache}, clicks)
    if not rows:
        print(f"   {jaw}: could not rank (needs at least 4 clicked teeth) - keeping the starter arch",
              flush=True)
        return start_case
    for i, (rms, case, n) in enumerate(rows[:3], 1):
        print(f"   {jaw} best #{i}: {os.path.basename(case)}   {rms:.2f} mm   ({n} teeth)", flush=True)
    return rows[0][1]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Upper + lower jaw overlay in one command")
    ap.add_argument("--case", default=do.DEFAULT_CASE, help="starter UPPER arch folder")
    ap.add_argument("--case-lower", default=None, help="starter LOWER arch folder (auto-found if omitted)")
    ap.add_argument("--photo", default=do.DEFAULT_PHOTO)
    ap.add_argument("--patient", default=None, help="dataset patient (folder or ID): no clicking")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--no-search", action="store_true")
    args = ap.parse_args(argv)

    print(f"run_both {do.VERSION}", flush=True)
    step(1, "Loading a starter upper arch and a starter lower arch ...")
    lower = args.case_lower or do.find_lower(args.case)[0]
    if not lower:
        raise SystemExit("No lower-arch folder found. Run  python check_lower.py  to see what is on "
                         "disk, or pass  --case-lower \"path\\to\\processed_part1_lower\\SOMECASE\"")
    starters = []
    for cd in (args.case, lower):
        print(f"   {cd}", flush=True)
        t = do.prepare_teeth(do.load_case(cd, quiet=True))
        starters.append((cd, t, do.anatomical_frame(t, quiet=True)))
    if starters[0][2]["upper"] == starters[1][2]["upper"]:
        raise SystemExit("The two folders are the same jaw - give one upper and one lower arch.")

    contours = {}
    clicks_by = {}
    if args.patient:
        step(2, "Reading the annotated tooth positions of the dataset photo (no clicking) ...")
        photo_path, cents, contours = do.load_patient(args.patient)
        photo = do.load_photo(photo_path)
        for cd, t, fr in starters:
            clicks_by[cd] = {f: p for f, p in cents.items() if f in t and f % 10 <= do.MAX_CLICK_INDEX}
    else:
        photo = do.load_photo(args.photo)
        step(2, "Click the teeth. First the first jaw, then a second window opens for the other jaw.")
        for idx, (cd, t, fr) in enumerate(starters):
            jaw = "UPPER" if fr["upper"] else "LOWER"
            print(f"   >>> NOW CLICK THE {jaw} TEETH in the window"
                  f"{'  (press K to skip this jaw)' if idx > 0 else ''}", flush=True)
            g = do.Guide(t, fr)
            got = do.collect_clicks(photo, g, allow_skip=(idx > 0))
            clicks_by[cd] = {f: p for f, p in got.items() if f in t}
            if len(clicks_by[cd]) < 4 and idx == 0:
                raise SystemExit("Fewer than 4 teeth clicked - run again.")

    step(3, "Choosing the best-matching arch for each jaw ..." if not args.no_search
         else "Skipping the arch search (--no-search): using the starter arches.")
    chosen = {}
    for cd, t, fr in starters:
        jaw = "upper" if fr["upper"] else "lower"
        if len(clicks_by[cd]) < 4:
            print(f"   {jaw}: fewer than 4 teeth - this jaw is left out", flush=True)
            continue
        best = cd if args.no_search else pick_best(jaw, cd, clicks_by[cd], args)
        chosen[cd] = best
        print(f"   {jaw} arch used: {os.path.basename(best)}", flush=True)
    if not chosen:
        raise SystemExit("Nothing to show - no jaw had enough teeth.")

    step(4, "Opening the fine-tune windows (photo + Controls) ...")
    items = []
    for cd, t, fr in starters:
        if cd not in chosen:
            continue
        best = chosen[cd]
        if best != cd:
            t = do.prepare_teeth(do.load_case(best, quiet=True))
            fr = do.anatomical_frame(t, quiet=True)
        sess = do.Session(t, fr, photo, clicks_by[cd], best,
                          contours={f: c for f, c in contours.items() if f in t} or None)
        g = do.Guide(t, fr)
        g.flip_u, g.flip_v = sess.flip_u, sess.flip_v
        g.rebuild()
        items.append((sess, g))
    parts = " ".join(f'--case{"" if do.jaw_name(s) == "upper" else "-lower"} "{s.case_dir}"'
                     for s, _ in items)
    print("   After pressing S, you can reopen this exact result without clicking again with:", flush=True)
    print(f'   python dental_overlay.py {parts} --clicks final_pose.json --photo "{args.photo}"', flush=True)
    do.run_gui(items[0][0], items[0][1], extra=items[1:])


if __name__ == "__main__":
    main()