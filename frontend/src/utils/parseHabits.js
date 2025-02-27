export function parseAnalysisToHabits(analysisText) {
  try {
    console.log("Texto original:", analysisText);

    // Encontra a seção "SUGGESTED HABITS:"
    const [_, habitsSection] = analysisText.split("SUGGESTED HABITS:");
    if (!habitsSection) {
      console.log("Seção de hábitos não encontrada");
      return [];
    }

    console.log("Seção de hábitos:", habitsSection);

    // Encontra todos os hábitos numerados
    const habitMatches = habitsSection.match(/\d+\.\s+(.*?)(?=\d+\.|$)/gs);
    if (!habitMatches) {
      console.log("Nenhum hábito encontrado");
      return [];
    }

    console.log("Hábitos encontrados:", habitMatches);

    return habitMatches.map((block, index) => {
      // Remove o número do início
      const cleanBlock = block.replace(/^\d+\.\s+/, "");

      // Extrai o título (primeira linha até Description:)
      const title = cleanBlock.split("Description:")[0].trim();

      // Extrai a descrição
      const descriptionMatch = cleanBlock.match(
        /Description:\s+(.*?)(?=How to Implement:|$)/s
      );
      const description = descriptionMatch ? descriptionMatch[1].trim() : "";

      // Extrai a implementação
      const implementationMatch = cleanBlock.match(
        /How to Implement:\s+(.*?)(?=Scientific Basis:|$)/s
      );
      const implementation = implementationMatch
        ? implementationMatch[1].trim()
        : "";

      // Extrai a base científica
      const scientificMatch = cleanBlock.match(/Scientific Basis:\s+(.*?)$/s);
      const scientific = scientificMatch ? scientificMatch[1].trim() : "";

      const habit = {
        id: index + 1,
        title,
        description,
        details: implementation,
        reference: {
          title: "Scientific Evidence",
          url: "#",
          publisher: scientific,
        },
        daysCompleted: [],
      };

      console.log("Hábito parseado:", habit);
      return habit;
    });
  } catch (error) {
    console.error("Erro ao parsear hábitos:", error);
    return [];
  }
}
