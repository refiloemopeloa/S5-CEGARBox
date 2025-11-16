#ifndef DIAMOND_H
#define DIAMOND_H

#include "../../Defines/Defines.h"
#include "../Box/Box.h"
#include "../FEnum/FEnum.h"
#include "../False/False.h"
#include "../Formula/Formula.h"
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <cassert>

using namespace std;

class Diamond : public Formula, public enable_shared_from_this<Diamond> {
private:

  //BOOLEAN INDICATOR FOR S5
  bool isS5Mode = false;

  int modality_, power_;
  int diaHash_ = -1;
  shared_ptr<Formula> subformula_;

public:
  //ADDED INDICATOR FOR S5
  Diamond(int modality, int power, shared_ptr<Formula> subformula, bool isS5);
  Diamond(int modality, int power, shared_ptr<Formula> subformula);
  ~Diamond();

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

  shared_ptr<Formula> constructDiamondReduced() const;

  //ADDED INDICATOR FOR S5
  static shared_ptr<Formula> create(int modality,
    int power,
    const shared_ptr<Formula> subformula
  );
  static shared_ptr<Formula> create(vector<int> modality,
    const shared_ptr<Formula> &subformula
  );

  //ADDED INDICATOR FOR S5
  static shared_ptr<Formula> create(int modality,
    int power,
    const shared_ptr<Formula> subformula,
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