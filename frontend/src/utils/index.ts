export const getTierColor = (tier) => {
  switch (tier) {
    case "Gold":
      return "#FFD700";
    case "Silver":
      return "#C0C0C0";
    case "Bronze":
      return "#CD7F32";
    case "Platinum":
      return "#E5E4E2";
    default:
      return "#757575";
  }
};

export const getScoreColor = (score) => {
  if (score >= 90) return "#4CAF50";
  if (score >= 70) return "#FF9800";
  return "#F44336";
};
