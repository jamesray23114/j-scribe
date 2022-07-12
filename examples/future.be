
main = { 
	putint(summation(1, 10, {10}));

	putint(max(1, 2));  // function call of the same name
	return 0; // or just 0
} 


func<int, int, func<int -> int> -> int> summation = [start, end, f] {  };

summation(1, 10, {1}); 					// returns 10