import runpy

scripts = [
    "scripts/1.2-compute-heavy-rain-months.py",
    "scripts/2.2-create-hand.py",
    "scripts/2.3-compute-hand.py",
    "scripts/2.4-classify-flood-prone.py",
    "scripts/3.1-combine-rainfall-hand-hazard.py",
    "scripts/4.2-compute-heatwave-days.py",
    "scripts/99-combine-hazards.py"
]

for script in scripts:
    print(f"\n=== Running: {script} ===")
    runpy.run_path(script, run_name="__main__")

print("\n✅ All steps complete!")
