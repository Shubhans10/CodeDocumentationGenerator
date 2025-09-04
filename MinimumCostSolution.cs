using System;
using System.Linq;

public class MinimumCostSolution
{
    public static long GetMinimumCost(int[] taskCosts, int operationsPerBundle, int bundleCost)
    {
        int n = taskCosts.Length;
        
        // Sort tasks by cost in descending order to prioritize removing expensive tasks
        int[] sortedCosts = taskCosts.OrderByDescending(x => x).ToArray();
        
        // Calculate prefix sums for efficient range sum queries
        long[] prefixSum = new long[n + 1];
        for (int i = 0; i < n; i++)
        {
            prefixSum[i + 1] = prefixSum[i] + sortedCosts[i];
        }
        
        long minCost = long.MaxValue;
        
        // Try all possible numbers of cleanup operations (0 to n)
        for (int operations = 0; operations <= n; operations++)
        {
            // Calculate number of bundles needed
            int bundlesNeeded = (operations + operationsPerBundle - 1) / operationsPerBundle; // Ceiling division
            long bundlesCost = (long)bundlesNeeded * bundleCost;
            
            // Calculate cost of retained tasks (sum of cheapest (n - operations) tasks)
            int retainedTasks = n - operations;
            long retainedCost = prefixSum[n] - prefixSum[operations]; // Sum from operations to n-1
            
            long totalCost = bundlesCost + retainedCost;
            minCost = Math.Min(minCost, totalCost);
        }
        
        return minCost;
    }
    
    // Test method with the provided example
    public static void Main(string[] args)
    {
        // Example from the problem
        int[] taskCosts = {7, 1, 6, 3, 6};
        int operationsPerBundle = 2;
        int bundleCost = 10;
        
        long result = GetMinimumCost(taskCosts, operationsPerBundle, bundleCost);
        Console.WriteLine($"Minimum cost: {result}");
        
        // Let's trace through the solution
        Console.WriteLine("\nDetailed analysis:");
        Console.WriteLine("Original costs: [7, 1, 6, 3, 6]");
        Console.WriteLine("Sorted costs (desc): [7, 6, 6, 3, 1]");
        Console.WriteLine("Operations per bundle: 2");
        Console.WriteLine("Bundle cost: 10");
        Console.WriteLine();
        
        // Show cost for each number of operations
        int[] sorted = taskCosts.OrderByDescending(x => x).ToArray();
        for (int ops = 0; ops <= taskCosts.Length; ops++)
        {
            int bundles = (ops + operationsPerBundle - 1) / operationsPerBundle;
            long bundlesCost = (long)bundles * bundleCost;
            long retainedCost = sorted.Skip(ops).Sum();
            long totalCost = bundlesCost + retainedCost;
            
            Console.WriteLine($"Operations: {ops}, Bundles: {bundles}, "+
                            $"Bundle cost: {bundlesCost}, Retained cost: {retainedCost}, "+
                            $"Total: {totalCost}");
        }
    }
}

/*
 * Solution Explanation:
 * 
 * 1. Sort tasks by cost in descending order to prioritize removing expensive tasks
 * 2. Use prefix sums for efficient calculation of retained task costs
 * 3. For each possible number of operations (0 to n):
 *    - Calculate bundles needed using ceiling division
 *    - Calculate cost of retained tasks (cheapest remaining tasks)
 *    - Track minimum total cost
 * 
 * Time Complexity: O(n log n) due to sorting
 * Space Complexity: O(n) for sorted array and prefix sums
 * 
 * For the example [7, 1, 6, 3, 6] with operationsPerBundle=2, bundleCost=10:
 * - Sorted: [7, 6, 6, 3, 1]
 * - Optimal: Use 2 operations (1 bundle) to remove tasks costing 7 and 6
 * - Retain tasks costing [6, 3, 1] = 10
 * - Total cost: 10 (bundle) + 10 (retained) = 20
 */