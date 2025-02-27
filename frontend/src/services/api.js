const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Analyze behavior and save to contract
export async function analyzeBehavior(behaviorData) {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        patient_id: behaviorData.patient_id,
        behavior: behaviorData.behavior,
        antecedent: behaviorData.antecedent,
        consequence: behaviorData.consequence,
        previous_attempts: behaviorData.previous_attempts,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error analyzing behavior:", error);
    throw error;
  }
}

// Create viewing key for a patient
export async function createViewingKey(patientId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/create-viewing-key/${patientId}`,
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error creating viewing key:", error);
    throw error;
  }
}

// Get analyses for a patient using viewing key
export async function getAnalyses(patientId, viewingKey) {
  try {
    if (!patientId || !viewingKey) {
      throw new Error("Patient ID and viewing key are required");
    }

    const url = `${API_BASE_URL}/analyses/${patientId}?viewing_key=${viewingKey}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      mode: "cors",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    return {
      analyses: data.analyses || [],
    };
  } catch (error) {
    console.error("Error fetching analyses:", error);
    return {
      analyses: [],
    };
  }
}
