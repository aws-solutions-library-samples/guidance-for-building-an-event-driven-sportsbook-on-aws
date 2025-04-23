/**
 * Converts decimal odds to fractional format
 * 
 * @param {number|string} decimal - The decimal odds to convert
 * @returns {string} - The odds in fractional format (e.g. "5/2")
 */
export const decimalToFraction = (decimal) => {
  // Handle edge cases
  if (decimal === undefined || decimal === null) return '';
  
  // Convert string to number if needed
  const decimalNum = typeof decimal === 'string' ? parseFloat(decimal) : decimal;
  
  // Handle invalid inputs
  if (isNaN(decimalNum) || decimalNum <= 1) return decimal?.toString() || '';
  
  // Common fractional odds mappings for better readability
  const commonOdds = {
    1.5: "1/2",
    1.67: "2/3",
    1.75: "3/4",
    2.0: "1/1",
    2.25: "5/4",
    2.5: "3/2",
    2.75: "7/4",
    3.0: "2/1",
    3.5: "5/2",
    4.0: "3/1",
    4.5: "7/2",
    5.0: "4/1",
    5.5: "9/2",
    6.0: "5/1",
    7.0: "6/1",
    8.0: "7/1",
    9.0: "8/1",
    10.0: "9/1",
    11.0: "10/1"
  };
  
  // Round to 2 decimal places for lookup
  const roundedDecimal = Math.round(decimalNum * 100) / 100;
  
  // Check if we have a common mapping
  if (commonOdds[roundedDecimal]) {
    return commonOdds[roundedDecimal];
  }
  
  // For odds not in our mapping, calculate the fraction
  // Subtract 1 to get the profit part
  const profit = decimalNum - 1;
  
  // Find a simple fraction approximation
  // For betting odds, we want simple fractions that are easy to understand
  let numerator = Math.round(profit * 100);
  let denominator = 100;
  
  // Simplify the fraction
  const gcd = (a, b) => b ? gcd(b, a % b) : a;
  const divisor = gcd(numerator, denominator);
  
  numerator = numerator / divisor;
  denominator = denominator / divisor;
  
  // Simplify complex fractions to more readable forms
  return simplifyFraction(numerator, denominator);
};

/**
 * Simplifies complex fractions to more readable forms
 * 
 * @param {number} numerator - The numerator of the fraction
 * @param {number} denominator - The denominator of the fraction
 * @returns {string} - The simplified fraction as a string
 */
const simplifyFraction = (numerator, denominator) => {
  // First, reduce the fraction to its simplest form
  const gcd = (a, b) => b ? gcd(b, a % b) : a;
  const divisor = gcd(numerator, denominator);
  
  numerator = numerator / divisor;
  denominator = denominator / divisor;
  
  // If the fraction is already simple (numerator <= 10 and denominator <= 10), return it
  if (numerator <= 10 && denominator <= 10) {
    return `${numerator}/${denominator}`;
  }
  
  // For complex fractions, find the closest simple fraction
  const decimalValue = numerator / denominator;
  
  // Common simple fractions and their decimal values
  const simpleFractions = [
    { fraction: "1/10", value: 0.1 },
    { fraction: "1/8", value: 0.125 },
    { fraction: "1/6", value: 0.1667 },
    { fraction: "1/5", value: 0.2 },
    { fraction: "1/4", value: 0.25 },
    { fraction: "1/3", value: 0.3333 },
    { fraction: "2/5", value: 0.4 },
    { fraction: "1/2", value: 0.5 },
    { fraction: "3/5", value: 0.6 },
    { fraction: "2/3", value: 0.6667 },
    { fraction: "3/4", value: 0.75 },
    { fraction: "4/5", value: 0.8 },
    { fraction: "5/6", value: 0.8333 },
    { fraction: "7/8", value: 0.875 },
    { fraction: "9/10", value: 0.9 },
    { fraction: "1/1", value: 1.0 },
    { fraction: "6/5", value: 1.2 },
    { fraction: "5/4", value: 1.25 },
    { fraction: "4/3", value: 1.3333 },
    { fraction: "3/2", value: 1.5 },
    { fraction: "8/5", value: 1.6 },
    { fraction: "5/3", value: 1.6667 },
    { fraction: "7/4", value: 1.75 },
    { fraction: "2/1", value: 2.0 },
    { fraction: "5/2", value: 2.5 },
    { fraction: "3/1", value: 3.0 },
    { fraction: "7/2", value: 3.5 },
    { fraction: "4/1", value: 4.0 },
    { fraction: "9/2", value: 4.5 },
    { fraction: "5/1", value: 5.0 },
    { fraction: "6/1", value: 6.0 },
    { fraction: "7/1", value: 7.0 },
    { fraction: "8/1", value: 8.0 },
    { fraction: "9/1", value: 9.0 },
    { fraction: "10/1", value: 10.0 }
  ];
  
  // Find the closest simple fraction
  let closestFraction = `${numerator}/${denominator}`;
  let minDifference = Number.MAX_VALUE;
  
  for (const sf of simpleFractions) {
    const difference = Math.abs(sf.value - decimalValue);
    if (difference < minDifference) {
      minDifference = difference;
      closestFraction = sf.fraction;
    }
  }
  
  // For complex fractions like 33/97 or 198/377, use a more aggressive simplification
  // If both numerator and denominator are large, always simplify
  if (numerator > 20 || denominator > 20) {
    // Use a higher tolerance (within 15%) for very complex fractions
    const tolerance = (numerator > 100 || denominator > 100) ? 0.15 : 0.1;
    
    if (minDifference / decimalValue <= tolerance) {
      return closestFraction;
    }
    
    // If we can't find a good match, try to simplify to a fraction with smaller numbers
    // For example, 198/377 ≈ 1/2 (within 15% error)
    const simpleApproximations = [
      { fraction: "1/10", value: 0.1 },
      { fraction: "1/5", value: 0.2 },
      { fraction: "1/4", value: 0.25 },
      { fraction: "1/3", value: 0.3333 },
      { fraction: "1/2", value: 0.5 },
      { fraction: "2/3", value: 0.6667 },
      { fraction: "3/4", value: 0.75 },
      { fraction: "1/1", value: 1.0 },
      { fraction: "3/2", value: 1.5 },
      { fraction: "2/1", value: 2.0 },
      { fraction: "5/2", value: 2.5 },
      { fraction: "3/1", value: 3.0 },
      { fraction: "4/1", value: 4.0 },
      { fraction: "5/1", value: 5.0 }
    ];
    
    for (const sf of simpleApproximations) {
      const difference = Math.abs(sf.value - decimalValue);
      if (difference / decimalValue <= tolerance) {
        return sf.fraction;
      }
    }
  }
  
  // If the fraction is still complex but not extremely so, use a moderate tolerance
  if ((numerator > 10 || denominator > 10) && minDifference / decimalValue <= 0.05) {
    return closestFraction;
  }
  
  // Otherwise, return the original reduced fraction
  return `${numerator}/${denominator}`;
};

/**
 * Converts fractional odds to decimal format
 * 
 * @param {string} fraction - The fractional odds (e.g. "5/2")
 * @returns {number} - The odds in decimal format
 */
export const fractionToDecimal = (fraction) => {
  // Handle edge cases
  if (!fraction || typeof fraction !== 'string' || !fraction.includes('/')) {
    return parseFloat(fraction) || 0;
  }
  
  const [numerator, denominator] = fraction.split('/').map(Number);
  
  // Handle invalid inputs
  if (isNaN(numerator) || isNaN(denominator) || denominator === 0) {
    return 0;
  }
  
  // Calculate decimal odds (add 1 to convert from decimal value to decimal odds)
  return (numerator / denominator) + 1;
};
