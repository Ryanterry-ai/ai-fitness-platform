# ── DIET GENERATOR ──────────────────────────────────────────────
@app.route("/diet", methods=["POST"])
@login_required
def diet():
    try:
        # Accept both form-data (for file upload) and JSON
        data = request.form.to_dict() if request.form else request.get_json(force=True)
        for key in ["weight", "height", "age"]:
            if key in data and data[key]:
                data[key] = float(data[key])

        # Get user
        with get_db() as conn:
            user = dict(conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone())

        # Merge user info + request
        merged = {**user, **data}

        # Handle BCA upload
        if "bca" in request.files:
            f = request.files["bca"]
            fname = f"{uid()}_bca_{int(time.time())}_{f.filename}"
            f.save(os.path.join(UPLOAD_DIR, fname))
            merged["bca_file"] = fname

        # Step 1: BMR
        weight = merged["weight"]
        height = merged["height"]
        age = merged["age"]
        sex = merged.get("sex", "male")
        bmr = 10*weight + 6.25*height - 5*age + (5 if sex=="male" else -161)

        # Step 2: TDEE
        activity_map = {"sedentary":1.2,"light":1.375,"moderate":1.55,"active":1.725,"very_active":1.9}
        tdee = bmr * activity_map.get(merged.get("activity","moderate"),1.55)

        # Step 3: Adjust calories
        goal = merged.get("goal","muscle_gain")
        if goal=="muscle_gain": calories = round(tdee+400)
        elif goal=="fat_loss": calories = round(tdee-400)
        else: calories = round(tdee)

        # Step 4: Generate diet
        plan = generate_diet(merged, calories)

        # Explanation
        explanation = f"BMR={round(bmr)} kcal, TDEE={round(tdee)} kcal, calories adjusted for goal={calories} kcal. Macros: Protein {plan['macros']['protein_g']}g, Carbs {plan['macros']['carbs_g']}g, Fats {plan['macros']['fats_g']}g."

        # Save plan
        import json
        with get_db() as conn:
            conn.execute("INSERT INTO diet_plans(user_id,plan_data,goal,calories,bca_file) VALUES (?,?,?,?,?)",
                         (uid(), json.dumps(plan), goal, calories, merged.get("bca_file")))

        return jsonify({
            "goal": goal,
            "total_calories": calories,
            "macros": plan["macros"],
            "meals": plan["meals"],
            "supplements": plan["supplements"],
            "notes": plan["notes"],
            "explanation": explanation
        })

    except Exception as e:
        print("Diet generator error:", e)
        return jsonify({"error": str(e)}),500
