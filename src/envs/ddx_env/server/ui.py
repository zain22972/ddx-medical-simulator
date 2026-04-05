import gradio as gr

def build_ui(env):
    def update_ui_state(obs, action_str="", reply=""):
        cc = obs['chief_complaint']
        symp = "\n\n".join([f"✔️ {s}" for s in obs['symptoms_revealed']]) or "*None discovered yet*"
        tests = "\n\n".join([f"🔬 {t}" for t in obs['tests_done']]) or "*None ordered yet*"
        score = float(obs['reward'] or 0.0)
        
        status = f"**Step:** {obs['step_count']} / {obs['step_count'] + obs['steps_remaining']} &nbsp;&nbsp;|&nbsp;&nbsp; **Overall Score:** {score:.2f} &nbsp;&nbsp;|&nbsp;&nbsp; **Finished:** {obs['done']}"
        
        if not action_str:
            banner = "### 🏥 Welcome Doctor! Patient is ready for evaluation."
        else:
            # Color code the result naturally using markdown emojis
            if "No finding" in reply or "not available" in reply:
                banner = f"### ❌ Action: `{action_str}`\n> **Result:** {reply} *(Penalty: -0.05)*"
            elif obs['done'] and score > 0:
                banner = f"### 🟢 DIAGNOSIS CORRECT!\n> **Result:** {reply}\n> **Final Score:** {score:.2f}"
            elif obs['done'] and score <= 0:
                banner = f"### 🔴 DIAGNOSIS INCORRECT.\n> **Result:** {reply}\n> **Final Score:** {score:.2f}"
            else:
                banner = f"### ✅ Action: `{action_str}`\n> **Result:** {reply}"

        return cc, symp, tests, status, banner

    def reset_env():
        obs = env.reset()
        return update_ui_state(obs)

    def step_env(action_type, action_value):
        if not action_value.strip():
            return [gr.update(), gr.update(), gr.update(), gr.update(), gr.update()]
            
        action_str = f"[{action_type}] {action_value}"
        obs = env.step(action_type, action_value)
        reply = obs['last_result']
        
        return update_ui_state(obs, action_str, reply)

    with gr.Blocks(title="DDx RL Environment") as ui:
        gr.Markdown("# 🏥 DDx Simulator: Sleek Dashboard")
        
        # Big dynamic event banner
        with gr.Row():
            with gr.Column(scale=1, variant="panel"):
                banner_display = gr.Markdown("### 🏥 Welcome Doctor! Patient is ready.")
        
        with gr.Row():
            # Left Column: Inputs
            with gr.Column(scale=1):
                gr.Markdown("### 1. Interact")
                action_type = gr.Radio(
                    choices=["ask_symptom", "order_test", "submit_diagnosis"], 
                    label="Action Type", 
                    value="ask_symptom"
                )
                action_value = gr.Textbox(
                    label="Medical Query",
                    placeholder="e.g. nausea, shortness of breath, ecg..."
                )
                
                with gr.Row():
                    step_btn = gr.Button("Submit Action", variant="primary")
                    reset_btn = gr.Button("New Patient", variant="secondary")
                
            # Right Column: Chart
            with gr.Column(scale=2, variant="panel"):
                status_display = gr.Markdown("...")
                gr.Markdown("---")
                gr.Markdown("**🩺 Chief Complaint:**")
                cc_display = gr.Markdown("...")
                gr.Markdown("**📝 Revealed Symptoms:**")
                symp_display = gr.Markdown("...")
                gr.Markdown("**🔬 Lab/Imaging Results:**")
                test_display = gr.Markdown("...")

        # Load events
        ui.load(fn=reset_env, outputs=[cc_display, symp_display, test_display, status_display, banner_display])
        reset_btn.click(fn=reset_env, outputs=[cc_display, symp_display, test_display, status_display, banner_display])
        
        action_value.submit(
            fn=step_env, 
            inputs=[action_type, action_value], 
            outputs=[cc_display, symp_display, test_display, status_display, banner_display]
        )
        step_btn.click(
            fn=step_env, 
            inputs=[action_type, action_value], 
            outputs=[cc_display, symp_display, test_display, status_display, banner_display]
        )

    return ui
