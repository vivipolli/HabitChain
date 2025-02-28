const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Create viewing key for a patient
export async function createViewingKey(patientId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/create-viewing-key/${patientId}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    // Store the viewing key in localStorage for future use
    localStorage.setItem(`viewing_key_${patientId}`, data.viewing_key);
    return data.viewing_key;
  } catch (error) {
    console.error("Error creating viewing key:", error);
    throw error;
  }
}

// Analyze behavior and save to contract
export async function analyzeBehavior(behaviorData) {
  try {
    // Ensure we have a viewing key
    let viewingKey = localStorage.getItem(
      `viewing_key_${behaviorData.patient_id}`
    );
    if (!viewingKey) {
      // If no viewing key exists, create one
      viewingKey = await createViewingKey(behaviorData.patient_id);
    }

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

// Get analyses for a patient
export async function getAnalyses(patientId) {
  try {
    if (!patientId) {
      throw new Error("Patient ID is required");
    }

    // Get viewing key from localStorage
    let viewingKey = localStorage.getItem(`viewing_key_${patientId}`);

    // If no viewing key exists, create one
    if (!viewingKey) {
      viewingKey = await createViewingKey(patientId);
    }

    const url = `${API_BASE_URL}/analyses/${patientId}?viewing_key=${viewingKey}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      // If viewing key is invalid, try to create a new one and retry
      if (response.status === 401 || response.status === 403) {
        viewingKey = await createViewingKey(patientId);
        const retryResponse = await fetch(
          `${API_BASE_URL}/analyses/${patientId}?viewing_key=${viewingKey}`,
          {
            method: "GET",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
          }
        );
        if (!retryResponse.ok) {
          throw new Error(`HTTP error! status: ${retryResponse.status}`);
        }
        return await retryResponse.json();
      }
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
