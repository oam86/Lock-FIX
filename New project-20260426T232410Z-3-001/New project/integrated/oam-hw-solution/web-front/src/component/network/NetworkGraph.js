import React from 'react';
import Chart from "react-apexcharts";
import "../../css/ApexChart.css";


class NetworkGraph extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      series: [],
      options: {
        chart: {
          type: 'area',
          stacked: false,
          height: 350,
          zoom: {
            type: 'x',
            enabled: true,
            autoScaleYaxis: true
          },

          toolbar: {
            autoSelected: 'zoom',
            tools: {
              download: true // 다운로드 버튼 활성화
            },
            export: {
              csv: {
                filename: '사용량 로그',
                headerCategory: 'category',
                categoryFormatter(x) {
                  return new Date(x).toLocaleString()
                },
                columnDelimiter: ',',
                // CSV 데이터를 커스터마이징 (날짜와 시간 모두 포함)
                dateFormatter: function (timestamp) {
                  return new Date(timestamp).toLocaleString(); // 날짜와 시간 모두 포함
                }
              }
              }

          }
        },
        dataLabels: {
          enabled: false
        },
        markers: {
          size: 0,
        },
        title: {
          text: '네트워크 I/O Utilization',
          align: 'left'
        },
        fill: {
          type: 'gradient',
          gradient: {
            shadeIntensity: 1,
            inverseColors: false,
            opacityFrom: 0.5,
            opacityTo: 0,
            stops: [0, 90, 100]
          },
        },
        yaxis: {
          labels: {
            formatter: function (val) {
              return `${val.toFixed(2)}%`; // 소수점 2자리까지 표시
            },
          },
          title: {
            text: '네트워크 사용량 (kb)'
          },
        },
        xaxis: {
          type: 'datetime',
          labels: {
            formatter: function (value) {
              // X축에는 날짜만 표시
              return new Date(value).toLocaleDateString(); // 날짜만 반환
            },
          },
          tooltip: {
            enabled: true,
            formatter: function (value) {
              // 툴팁에는 날짜와 시간을 모두 표시
              return new Date(value).toLocaleString(); // 날짜와 시간 모두 반환
            }
          }
        },

        tooltip: {
          shared: false,
          x: {
            format: 'yyyy-MM-dd HH:mm:ss' // 툴팁에서 시간 포함
          },
          y: {
            formatter: function (val) {
              return `${val}%`;
            }
          }
        },
        legend: {
          show: true,
          position: 'top',
          horizontalAlign: 'center',
          formatter: function (seriesName, opts) {
            return `<span>${seriesName}</span><span class="vertical-divider"></span>`;
          },
          onItemClick: {
            toggleDataSeries: true,
          },
          onItemHover: {
            highlightDataSeries: true,
          },
        },
      }
    };
  }

  componentDidMount() {
    if (Array.isArray(this.props.data)) {
      this.setState({ series: this.props.data });
    } else {
      console.error("Invalid data format for HwGraph. Expected an array of series.");
    }
  }

  componentDidUpdate(prevProps) {
    // Props가 업데이트될 때 새로운 데이터를 반영
    if (this.props.data !== prevProps.data && Array.isArray(this.props.data)) {
      this.setState({ series: this.props.data });
    }
  }

  render() {
    return (
      <div>
        <div id="chart">
          <Chart options={this.state.options} series={this.state.series.length ? this.state.series : [{ name: "No Data", data: [] }]} type="area" height={350} />
        </div>
      </div>
    );
  }
}

export default NetworkGraph;