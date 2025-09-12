import React from "react";
import { ResponsiveBar } from "@nivo/bar";

const TopMerchantsBar = ({ rows = [] }) => {
  return (
    <div style={{ height: 360 }}>
      <ResponsiveBar
        data={rows}
        indexBy="merchant"
        keys={["amount"]}
        margin={{ top: 20, right: 20, bottom: 80, left: 60 }}
        padding={0.3}
        colors={{ scheme: "nivo" }}
        axisBottom={{ tickRotation: -45 }}
        axisLeft={{ legend: "Amount", legendOffset: -50, legendPosition: "middle" }}
        labelSkipWidth={12}
        labelSkipHeight={12}
        enableGridY
      />
    </div>
  );
};

export default TopMerchantsBar;


