import axios from "axios";

// Função para salvar dados na rede Sonic
export async function saveDataToSonic(dataType, data) {
  try {
    // Aqui fazemos uma chamada para o backend que irá interagir com a rede Sonic
    const response = await axios.post("/api/sonic/save", {
      dataType, // 'userInput' ou 'aiAnalysis'
      data,
    });

    console.log(`Dados do tipo ${dataType} salvos com sucesso na rede Sonic`);
    return response.data.transactionHash;
  } catch (error) {
    console.error(`Erro ao salvar dados na rede Sonic: ${error.message}`);
    throw error;
  }
}

// Função específica para salvar o input do usuário
export async function saveUserInputToSonic(userInput) {
  return saveDataToSonic("userInput", userInput);
}

// Função específica para salvar a análise da IA
export async function saveAIAnalysisToSonic(analysis) {
  return saveDataToSonic("aiAnalysis", analysis);
}

// Função para recuperar dados da rede Sonic
export async function getDataFromSonic(dataType, address) {
  try {
    const response = await axios.get(`/api/sonic/get`, {
      params: {
        dataType,
        address,
      },
    });

    return response.data;
  } catch (error) {
    console.error(`Erro ao recuperar dados da rede Sonic: ${error.message}`);
    throw error;
  }
}
