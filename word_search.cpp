#include<vector>
#include<string.h>
#include<string>
#include<vector>
#include<iostream>
using namespace std;

class Solution {
	public:
		int move[4][2] = {{1,0} , {-1,0} , {0,1} , {0,-1}};
		int  b_row, b_col;

		bool judge_exist(vector<vector<char> >& board, string word) {
			if(word.size() == 0) {
				return true;
			}
			if(board.size() == 0 || board[0].size() == 0) {
				return false;
			}
			b_row = board.size();
			b_col = board[0].size();

			vector<vector<bool> > find = {{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}};
			int s_row=0, s_col=0;
			for(s_row = 0; s_row<b_row; s_row++ ) {
				for (s_col = 0; s_col<b_col; s_col++) {
					if(search_word(0, board, word, find, s_row, s_col)) {
						return true;
					}
				}
			}
			return false;
		}

		bool search_word(int s_len, vector<vector<char> > board, string word,  vector<vector<bool> > find, int a, int b) {
			if (s_len == word.size()) {
				return true;
			}
			if(a < 0 || a == b_row || b < 0 || b== b_col )  {
				return false;
			} else if(find[a][b] || board[a][b] != word[s_len] ) {
				return false;
			}
			find[a][b] = 1;
			for (int i = 0; i<4; i++) {
				if (search_word(s_len+1,board,word,find,a+move[i][0],b+move[i][1])) {
					return true;
				}
			}
			find[a][b]= 0;
			return false;
		}


};

int main(void) {
	vector<vector<char>> board = {
		{'A', 'B', 'C', 'E'},
		{'S', 'F', 'C', 'S'},
		{'A', 'D', 'E', 'E'}
	};
	string word = "ABCCED";
	Solution test;
	bool result = test.judge_exist(board, word);
	return 0;
}
