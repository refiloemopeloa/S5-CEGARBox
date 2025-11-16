#ifndef BOX_H
#define BOX_H

#include "../../Defines/Defines.h"
#include "../Diamond/Diamond.h"
#include "../FEnum/FEnum.h"
#include "../Formula/Formula.h"
#include "../True/True.h"
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

using namespace std;

class Box : public Formula, public enable_shared_from_this<Box> {
private:

  //BOOLEAN INDICATOR FOR S5
  bool isS5Mode = false;

  int modality_, power_;
  shared_ptr<Formula> subformula_;
  int boxHash_;

public:
  //ADDED INDICATOR FOR S5
  Box(int modality, int power, shared_ptr<Formula> subformula, bool isS5);
  Box(int modality, int power, shared_ptr<Formula> subformula);
  ~Box();

  //GETTER FOR S5
  bool getIsS5Mode() const;

  int getModality() const;
  int getPower() const;
  shared_ptr<Formula> getSubformula() const;

  void incrementPower();

  string toString() const;
  FormulaType getType() const;

  shared_ptr<Formula> negatedNormalForm();
  shared_ptr<Formula> tailNormalForm();
  shared_ptr<Formula> negate();
  shared_ptr<Formula> simplify();
  shared_ptr<Formula> simplifyS5(); //SPECIAL S5 SIMPLIFIER
  shared_ptr<Formula> modalFlatten();
  shared_ptr<Formula> axiomSimplify(int axiom, int depth);

  shared_ptr<Formula> clone() const;
  shared_ptr<Formula> constructBoxReduced() const;

  static shared_ptr<Formula> create(int modality,
    int power,
    const shared_ptr<Formula> &subformula
  );
  static shared_ptr<Formula> create(vector<int> modality,
    const shared_ptr<Formula> &subformula
  );
 
  //CREATING OPERATORS FOR S5 MODALITIES
  static shared_ptr<Formula> create(int modality,
    int power,
    const shared_ptr<Formula> &subformula,
    bool isS5
  );
  static shared_ptr<Formula> create(vector<int> modality,
    const shared_ptr<Formula> &subformula,
    bool isS5
  );

  bool operator==(const Formula &other) const;
  bool operator!=(const Formula &other) const;

  size_t hash() const;
};

#endif