const form = document.querySelector("#generate-form");
const results = document.querySelector("#results");

function fillList(id, values) {
  const node = document.querySelector(id);
  node.innerHTML = "";
  const list = values && values.length ? values : ["None identified"];
  for (const value of list) {
    const li = document.createElement("li");
    li.textContent = value;
    node.appendChild(li);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = form.querySelector("button");
  button.disabled = true;
  button.textContent = "Generating...";

  const data = new FormData(form);
  const payload = {
    role_title: data.get("role_title") || null,
    company_name: data.get("company_name") || null,
    job_description: data.get("job_description"),
    refresh_profile: data.get("refresh_profile") === "on",
  };

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Generation failed");
    }
    const result = await response.json();
    document.querySelector("#score").textContent = `${result.match_score}%`;
    fillList("#matched", result.matched_skills);
    fillList("#missing", result.missing_skills);
    fillList("#feedback", result.feedback);
    document.querySelector("#resume-link").href = result.resume_url;
    document.querySelector("#cover-link").href = result.cover_letter_url;
    results.hidden = false;
  } catch (error) {
    alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Generate Resume";
  }
});

