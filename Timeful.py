import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Smart Scheduler", page_icon="🧠")

st.title("🧠 Smart Scheduler")
st.write("Automatically schedule your tasks into free time slots.")

# Input: Busy slots
st.subheader("Your busy times")
if "busy" not in st.session_state:
    st.session_state.busy = []

start_busy = st.time_input("Start busy time", datetime.now().replace(hour=9, minute=0).time())
end_busy = st.time_input("End busy time", datetime.now().replace(hour=10, minute=0).time())
if st.button("Add busy slot"):
    st.session_state.busy.append((start_busy, end_busy))
for s, e in st.session_state.busy:
    st.write(f"🕒 {s.strftime('%H:%M')}–{e.strftime('%H:%M')}")

# Input: Tasks
st.subheader("Your tasks")
if "tasks" not in st.session_state:
    st.session_state.tasks = []

name = st.text_input("Task name")
duration = st.number_input("Duration (hours)", min_value=0.5, step=0.5)
deadline = st.date_input("Deadline")
if st.button("Add task"):
    st.session_state.tasks.append({"name": name, "duration": duration, "deadline": datetime.combine(deadline, datetime.min.time())})
for t in st.session_state.tasks:
    st.write(f"📋 {t['name']} – {t['duration']}h (by {t['deadline'].strftime('%Y-%m-%d')})")

# Scheduling function
def find_free_slots(busy, start, end):
    free = []
    current = start
    for b_start, b_end in sorted(busy):
        if current < b_start:
            free.append((current, b_start))
        current = max(current, b_end)
    if current < end:
        free.append((current, end))
    return free

def schedule_tasks(tasks, busy_slots, work_start, work_end):
    free_slots = find_free_slots(busy_slots, work_start, work_end)
    scheduled = []
    for task in sorted(tasks, key=lambda x: x['deadline']):
        duration = timedelta(hours=task['duration'])
        for i, (slot_start, slot_end) in enumerate(free_slots):
            if slot_end - slot_start >= duration:
                scheduled.append({
                    "task": task['name'],
                    "start": slot_start,
                    "end": slot_start + duration
                })
                free_slots[i] = (slot_start + duration, slot_end)
                break
    return scheduled

# Generate schedule
st.subheader("Generate your schedule")
work_start = datetime.now().replace(hour=8, minute=0)
work_end = datetime.now().replace(hour=20, minute=0)

if st.button("Generate schedule"):
    busy_dt = [(datetime.combine(datetime.today(), s), datetime.combine(datetime.today(), e)) for s, e in st.session_state.busy]
    schedule = schedule_tasks(st.session_state.tasks, busy_dt, work_start, work_end)
    if schedule:
        st.success("✅ Schedule generated!")
        for s in schedule:
            st.write(f"📌 **{s['task']}** → {s['start'].strftime('%H:%M')} to {s['end'].strftime('%H:%M')}")
    else:
        st.warning("No available slots found.")
