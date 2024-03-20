import React, { useState, useEffect } from 'react';
import backgroundImage from '../assets/region_map.png';
import { usePingInfo } from "../hooks/usePingInfo";

const EdgePoint = ({ x, y, location, latency }) => {
  const [isHovering, setIsHovering] = useState(false);

  const handleMouseEnter = () => {
    setIsHovering(true);
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
  };

  return (
    <g>
      {isHovering && latency !== null && (
        <g>
          <rect
            x={x + 10}
            y={y - 40}
            width="200"
            height="60"
            fill="#333333"
            rx="10"
            ry="10"
            style={{
              filter: "drop-shadow(0 0 5px rgba(0, 0, 0, 0.3))",
            }}
          />
          <polygon
            points={`${x + 15},${y - 20} ${x + 30},${y - 20} ${x + 20},${y}`}
            fill="#333333"
            style={{
              filter: "drop-shadow(0 0 5px rgba(0, 0, 0, 0.3))",
            }}
          />
          <text x={x + 20} y={y - 25} fontSize="14" fill="#ffffff">
            {location}
          </text>
          <text x={x + 20} y={y - 10} fontSize="12" fill="#ffffff">
            Latency to Frankfurt: {latency}ms
          </text>
        </g>
      )}
      <circle
        cx={x}
        cy={y}
        r="5"
        fill="#00a8e1"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      />
    </g>
  );
};

export const EdgeMap = (isLocked) => {
  const { data: pingInfo, isLoading: loadingPingInfo } = usePingInfo();
  if (loadingPingInfo) return <div>Loading PingInfo</div>;
  if (!Array.isArray(pingInfo.items) || !pingInfo.items.length) {
    // Handle the case when pingInfo is not an array or is an empty array
    return <div>No ping information available</div>;
  }

  const edgePoints = [
    { x: 460, y: 180, location: 'us-east-1', locationName: 'Northern Virginia' },
    { x: 375, y: 180, locationName: 'Oregon', location: 'us-west-2' },
    { x: 830, y: 180, locationName: 'Tokyo', location: 'ap-northeast-1' },
    { x: 586, y: 175, locationName: 'Spain', location: 'eu-west-2' },
    { x: 770, y: 240, locationName: 'Singapore', location: 'ap-southeast-1' },
    // Add more edge points as needed
  ];

  return (
    <svg width="1200" height="400">
      <image href={backgroundImage} x="0" y="0" width="1200" height="400" />
      {pingInfo.items.map((pingPoint, index) => {
        const edgePoint = edgePoints.find(
          point => point.location === pingPoint.pingLocation
        );

        return (
          <EdgePoint
            key={index}
            x={edgePoint.x}
            y={edgePoint.y}
            location={edgePoint.locationName}
            latency={pingPoint.pingLatency}
          />
        )
      })}
    </svg>
  );
};

export default EdgeMap;