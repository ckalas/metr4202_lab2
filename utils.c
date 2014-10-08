#include <stdbool.h>
#include <stdio.h>

// clang -shared -dynamiclib -std=gnu99 utils.c -o utils.dylib

bool inArray(int val, int *arr, int size){
    int i;
    for (i=0; i < size; i++) {
        if (arr[i] == val)
            return true;
    }
    return false;
}

int checkNewPoint(int *match, int *xs, int *ys, int len) {
	for (int i = -20; i < 20; i++) {
		for (int j = -20; j < 20; j++) {
			if (inArray((match[0]+i),xs,len) && inArray((match[1]+j),ys,len)) {
				return 0;
			}
		}
	}
	return 1;
}

