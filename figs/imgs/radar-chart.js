document.addEventListener("DOMContentLoaded", function () {
  const chartDom = document.getElementById("radar-chart");
  if (!chartDom) return;

  if (typeof echarts === "undefined") {
    chartDom.innerHTML = "Radar chart failed to load because ECharts is unavailable.";
    chartDom.style.display = "grid";
    chartDom.style.placeItems = "center";
    chartDom.style.color = "#6b7280";
    return;
  }

  const myChart = echarts.init(chartDom, null, { renderer: "svg" });
  const categories = [
    { display: "Frame-Only", tooltip: "Frame-Only" },
    { display: "Frames & Audio", tooltip: "Frames & Audio" },
    { display: "Action & Motion", tooltip: "Action & Motion" },
    { display: "Order", tooltip: "Order" },
    { display: "Change", tooltip: "Change" },
    { display: "Temporal\nReasoning", tooltip: "Temporal Reasoning" },
    {
      display: "Complex Plot\nComprehension",
      tooltip: "Complex Plot Comprehension",
    },
    {
      display: "Video-Based\nKnowledge Acquisition",
      tooltip: "Video-Based Knowledge Acquisition",
    },
    {
      display: "Social Behavior\nAnalysis",
      tooltip: "Social Behavior Analysis",
    },
    {
      display: "Physical World\nReasoning",
      tooltip: "Physical World Reasoning",
    },
  ];

  const cwIndices = [0, 9, 8, 7, 6, 5, 4, 3, 2, 1];
  const indicatorNames = cwIndices.map((i) => categories[i].display);
  const tooltipNames = cwIndices.map((i) => categories[i].tooltip);
  const numAxes = categories.length;

  const colors = {
    "Human Expert": "#2F3B44",
    "Gemini-3-Pro": "#426466",
    "GPT-5": "#648688",
    "Doubao-Seed-2.0-Pro-260215": "#86A8AA",
    "Qwen3-Omni-30B-A3B-Instruct": "#A05A58",
    "Qwen3-VL-235B-A22B-Instruct": "#B87572",
    "InternVL3-5-241B-A28B-Instruct": "#CE8F8C",
  };

  const legendLabels = {
    "Human Expert": "Human Expert",
    "Gemini-3-Pro": "Gemini-3-Pro",
    "GPT-5": "GPT-5",
    "Doubao-Seed-2.0-Pro-260215": "Doubao-Seed-2.0-Pro\n260215",
    "Qwen3-Omni-30B-A3B-Instruct": "Qwen3-Omni-30B-A3B\nInstruct",
    "Qwen3-VL-235B-A22B-Instruct": "Qwen3-VL-235B-A22B\nInstruct",
    "InternVL3-5-241B-A28B-Instruct": "InternVL3-5-241B-A28B\nInstruct",
  };

  let userLegendState = {
    "Human Expert": true,
    "Gemini-3-Pro": true,
    "GPT-5": true,
    "Doubao-Seed-2.0-Pro-260215": true,
    "Qwen3-Omni-30B-A3B-Instruct": true,
    "Qwen3-VL-235B-A22B-Instruct": true,
    "InternVL3-5-241B-A28B-Instruct": true,
  };

  const rawData = [
    {
      name: "Human Expert",
      value: [96.1589, 93.6332, 89.0858, 92.9444, 95.1923, 87.2727, 87.0929, 89.9665, 91.6111, 84.1246],
      meta: {
        overallAcc: 0.9494,
        nonLinScore: 90.6786,
        consistencyScore: 91.6667,
        coherenceScore: 88.8538,
        level1Score: 94.8276,
        level2Score: 91.1228,
        level3Score: 87.9406,
      },
    },
    {
      name: "Gemini-3-Pro",
      value: [47.1, 68.26, 24.14, 55.41, 43.63, 43.17, 36.53, 44.26, 36.43, 20.94],
    },
    {
      name: "GPT-5",
      value: [27.34, 32.65, 15.22, 29.78, 31.73, 26.66, 22.24, 26.44, 19.83, 15.05],
    },
    {
      name: "Doubao-Seed-2.0-Pro-260215",
      value: [53.48, 55.31, 27.24, 65.83, 45.43, 46.79, 37.19, 43.07, 36.52, 21.63],
    },
    {
      name: "Qwen3-Omni-30B-A3B-Instruct",
      value: [19.28, 23.8, 11.38, 19.16, 11.18, 17.2, 17.65, 18.3, 18.02, 10.92],
    },
    {
      name: "Qwen3-VL-235B-A22B-Instruct",
      value: [24.37, 36.42, 13.99, 31.13, 24.64, 31.26, 22.88, 27.19, 24.51, 13.35],
    },
    {
      name: "InternVL3-5-241B-A28B-Instruct",
      value: [22.65, 33.14, 15.39, 28.17, 21.03, 30.37, 19.81, 21.52, 22.02, 15.97],
    },
  ];

  const modelNames = rawData.map((item) => item.name);
  let hoveredAxisIndex = 0;
  let currentHighlight = null;
  let resizeTimer = null;

  function getLayout() {
    const mobile = chartDom.clientWidth <= 860;
    return {
      mobile,
      center: mobile ? ["50%", "37%"] : ["37%", "45.5%"],
      radarRadius: mobile ? "59%" : "53%",
      ringInnerRadius: mobile ? "61%" : "55%",
      ringOuterRadius: mobile ? "69%" : "63%",
      legend: mobile
        ? {
            type: "scroll",
            orient: "horizontal",
            left: "center",
            top: "73%",
            width: "92%",
            itemGap: 10,
          }
        : {
            type: "plain",
            orient: "vertical",
            left: "76%",
            top: "middle",
            width: "18%",
            itemGap: 12,
          },
      nameGap: mobile ? 18 : 14,
      labelFontSize: mobile ? 11 : 11.5,
      legendFontSize: mobile ? 10.5 : 11.5,
      ringGapSize: mobile ? 5 : 8,
      symbolSize: mobile ? 6 : 7,
    };
  }

  function percentToPixel(value, total) {
    if (typeof value === "string" && value.endsWith("%")) {
      return (parseFloat(value) / 100) * total;
    }
    return Number(value);
  }

  function getRadarCenterPixels(layout) {
    return {
      x: percentToPixel(layout.center[0], myChart.getWidth()),
      y: percentToPixel(layout.center[1], myChart.getHeight()),
    };
  }

  function updateHoveredAxisIndex(params) {
    const layout = getLayout();
    const center = getRadarCenterPixels(layout);
    const dx = params.offsetX - center.x;
    const dy = params.offsetY - center.y;
    let angle = Math.atan2(dy, dx) + Math.PI / 2;
    if (angle < 0) angle += Math.PI * 2;
    const sliceAngle = (Math.PI * 2) / numAxes;
    hoveredAxisIndex = Math.round((Math.PI * 2 - angle) / sliceAngle) % numAxes;
  }

  function buildSeriesData(highlightedModel) {
    return rawData.map((item) => {
      const isHighlighted = highlightedModel === item.name;
      const dimOthers = Boolean(highlightedModel) && !isHighlighted;
      const orderedValues = cwIndices.map((index) => item.value[index]);
      const isHumanExpert = item.name === "Human Expert";

      return {
        name: item.name,
        value: orderedValues,
        meta: item.meta,
        symbol: "circle",
        symbolSize: getLayout().symbolSize,
        itemStyle: {
          color: colors[item.name],
          opacity: dimOthers ? 0.22 : 1,
          borderColor: "#ffffff",
          borderWidth: isHumanExpert ? 1.6 : isHighlighted ? 1.2 : 0.8,
        },
        lineStyle: {
          color: colors[item.name],
          width: isHumanExpert ? 3.2 : isHighlighted ? 4 : 2.5,
          opacity: dimOthers ? 0.18 : 0.96,
          shadowBlur: isHighlighted || isHumanExpert ? 14 : 0,
          shadowColor: isHighlighted || isHumanExpert ? colors[item.name] : "transparent",
        },
        areaStyle: {
          color: colors[item.name],
          opacity: isHumanExpert ? 0.05 : isHighlighted ? 0.2 : dimOthers ? 0.03 : 0.08,
        },
      };
    });
  }

  function buildOption() {
    const layout = getLayout();

    return {
      animationDuration: 500,
      color: modelNames.map((name) => colors[name]),
      tooltip: {
        trigger: "item",
        confine: true,
        backgroundColor: "rgba(255,255,255,0.96)",
        borderColor: "#d1d5db",
        borderWidth: 1,
        textStyle: {
          color: "#111827",
          fontSize: 12,
        },
        formatter: function (params) {
          if (!Array.isArray(params.value)) return params.name;
          const idx = hoveredAxisIndex || 0;
          const value = Number(params.value[idx]).toFixed(2);
          const overall = params.data && params.data.meta && typeof params.data.meta.overallAcc === "number"
            ? `<div style="margin-top:4px; color:#6b7280;">Overall Acc: ${(params.data.meta.overallAcc * 100).toFixed(2)}</div>`
            : "";
          return [
            "<div style=\"min-width:180px;\">",
            `<div style="font-weight:700; margin-bottom:4px;">${params.name}</div>`,
            `<div style="color:#4b5563;">${tooltipNames[idx]}</div>`,
            `<div style="margin-top:4px; color:${colors[params.name]}; font-weight:700;">${value}</div>`,
            overall,
            "</div>",
          ].join("");
        },
      },
      legend: {
        ...layout.legend,
        icon: "circle",
        itemWidth: 12,
        itemHeight: 12,
        align: "left",
        padding: layout.mobile ? [10, 12] : [18, 18],
        backgroundColor: "rgba(255,255,255,0.94)",
        borderColor: "#d6d9de",
        borderWidth: 1,
        borderRadius: 14,
        shadowBlur: 18,
        shadowColor: "rgba(15, 23, 42, 0.08)",
        selected: userLegendState,
        data: modelNames,
        formatter: function (name) {
          return legendLabels[name] || name;
        },
        textStyle: {
          fontSize: layout.legendFontSize,
          color: "#2f3b44",
          lineHeight: layout.mobile ? 16 : 18,
          width: layout.mobile ? 96 : 150,
          overflow: "break",
        },
      },
      radar: {
        z: 3,
        center: layout.center,
        radius: layout.radarRadius,
        shape: "polygon",
        splitNumber: 5,
        nameGap: layout.nameGap,
        axisName: {
          color: "#334155",
          fontWeight: 700,
          fontSize: layout.labelFontSize,
          backgroundColor: "rgba(255,255,255,0.95)",
          borderColor: "#d1d5db",
          borderWidth: 1,
          borderRadius: 6,
          padding: layout.mobile ? [4, 7] : [3, 6],
          lineHeight: layout.mobile ? 14 : 16,
        },
        splitArea: {
          areaStyle: {
            color: ["rgba(255,255,255,0.00)"],
          },
        },
        splitLine: {
          lineStyle: {
            color: "#d5dbe3",
            type: "dashed",
            width: 1,
          },
        },
        axisLine: {
          lineStyle: {
            color: "#d5dbe3",
            type: "dashed",
            width: 1,
          },
        },
        indicator: indicatorNames.map((name) => ({
          name: name,
          max: 90,
        })),
      },
      series: [
        {
          type: "pie",
          z: 1,
          radius: [layout.ringInnerRadius, layout.ringOuterRadius],
          center: layout.center,
          startAngle: 90 + 180 / numAxes,
          clockwise: true,
          silent: true,
          label: { show: false },
          itemStyle: {
            borderColor: "#ffffff",
            borderWidth: layout.ringGapSize,
          },
          data: [
            {
              value: 2,
              name: "Level 1",
              itemStyle: { color: "#E4F3DD" },
            },
            {
              value: 4,
              name: "Level 2",
              itemStyle: { color: "#E0EDF5" },
            },
            {
              value: 4,
              name: "Level 3",
              itemStyle: { color: "#FCE2D1" },
            },
          ],
        },
        {
          type: "radar",
          z: 5,
          data: buildSeriesData(currentHighlight),
          emphasis: {
            disabled: true,
          },
        },
      ],
    };
  }

  function renderChart() {
    myChart.setOption(buildOption(), true);
  }

  function highlightModel(modelName) {
    if (currentHighlight === modelName) return;
    currentHighlight = modelName;
    myChart.setOption({
      series: [{}, { data: buildSeriesData(modelName) }],
    });
  }

  function restoreModels() {
    if (!currentHighlight) return;
    currentHighlight = null;
    myChart.setOption({
      series: [{}, { data: buildSeriesData(null) }],
    });
  }

  myChart.getZr().on("mousemove", updateHoveredAxisIndex);

  myChart.on("legendselectchanged", function (params) {
    userLegendState = { ...params.selected };
    if (currentHighlight && userLegendState[currentHighlight] === false) {
      restoreModels();
    }
  });

  myChart.on("mouseover", function (params) {
    if (params.seriesType === "radar" && modelNames.includes(params.name)) {
      highlightModel(params.name);
    }
  });

  myChart.on("mouseout", function (params) {
    if (params.seriesType === "radar" && modelNames.includes(params.name)) {
      restoreModels();
    }
  });

  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(function () {
      myChart.resize();
      renderChart();
    }, 120);
  });

  renderChart();
});
