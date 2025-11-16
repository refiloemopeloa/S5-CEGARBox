#include "Diamond.h"

//ADDED S5 INDICATOR HERE
Diamond::Diamond(int modality, int power, shared_ptr<Formula> subformula, bool isS5) {
  
  modality_ = modality;
  power_ = power;
  isS5Mode = isS5; //SETTING INDICATOR

  Diamond *diamondFormula = dynamic_cast<Diamond *>(subformula.get());
  if (diamondFormula) {
    if (diamondFormula->getModality() == modality_) {
      power_ += diamondFormula->getPower();
      subformula_ = diamondFormula->getSubformula();
    } else {
      subformula_ = subformula;
    }
  } else {
    subformula_ = subformula;
  }
  std::hash<FormulaType> ftype_hash;
  std::hash<int> int_hash;
  size_t totalHash = ftype_hash(getType());
  diaHash_ = totalHash + int_hash(modality_) + int_hash(power_) +
         subformula_->hash();
}

Diamond::Diamond(int modality, int power, shared_ptr<Formula> subformula) {
  
  modality_ = modality;
  power_ = power;

  Diamond *diamondFormula = dynamic_cast<Diamond *>(subformula.get());
  if (diamondFormula) {
    if (diamondFormula->getModality() == modality_) {
      power_ += diamondFormula->getPower();
      subformula_ = diamondFormula->getSubformula();
    } else {
      subformula_ = subformula;
    }
  } else {
    subformula_ = subformula;
  }
  std::hash<FormulaType> ftype_hash;
  std::hash<int> int_hash;
  size_t totalHash = ftype_hash(getType());
  diaHash_ = totalHash + int_hash(modality_) + int_hash(power_) +
         subformula_->hash();
}

Diamond::~Diamond() {
#if DEBUG_DESTRUCT
  cout << "DESTRUCTING DIAMOND" << endl;
#endif
}

bool Diamond::getIsS5Mode() const { return isS5Mode; } //ADDED THIS

int Diamond::getModality() const { return modality_; }

int Diamond::getPower() const { return power_; }

shared_ptr<Formula> Diamond::getSubformula() const { return subformula_; }

void Diamond::incrementPower() { power_++; }

string Diamond::toString() const {
    string ret = "";
    for (int i = 0; i < power_; ++i) ret += "<" + to_string(modality_) + ">";
    return ret + subformula_->toString();
}

FormulaType Diamond::getType() const { return FDiamond; }

shared_ptr<Formula> Diamond::negatedNormalForm() {
  subformula_ = subformula_->negatedNormalForm();
  return shared_from_this();
}

shared_ptr<Formula> Diamond::tailNormalForm() {
    assert (1 == 0);
}

//ADDED S5 INDICATOR HERE
shared_ptr<Formula> Diamond::negate() {
  return Box::create(modality_, power_, subformula_->negate(), getIsS5Mode());
}

//SEND TO S5SIMPLIFY IF NECESSARY
shared_ptr<Formula> Diamond::simplify() {

  if (getIsS5Mode()) return simplifyS5();

  subformula_ = subformula_->simplify();

  switch (subformula_->getType()) {
  case FFalse:
    return False::create();
  case FDiamond: {
    Diamond *diamondFormula = dynamic_cast<Diamond *>(subformula_.get());
    if (diamondFormula->getModality() == modality_) {
      power_ += diamondFormula->getPower();
      subformula_ = diamondFormula->getSubformula();
    }
    return shared_from_this();
  }

  default:
    return shared_from_this();
  }
}

//S5 SIMPLIFY
shared_ptr<Formula> Diamond::simplifyS5() {

  shared_ptr<Formula> newSubformula = subformula_->simplify();
  
  //S5 REDUCTION: ◇□φ → □φ
  if (newSubformula->getType() == FBox) {
      Box* box = dynamic_cast<Box*>(newSubformula.get());
      
      //RECURSIVELY SIMPLIFY THE RESULT
      return Box::create(box->getModality(),
        getPower() + box->getPower(),
        box->getSubformula(), 
        getIsS5Mode()
      )->simplify();
  }
  
  //S5 REDUCTION: ◇◇φ → ◇φ
  if (newSubformula->getType() == FDiamond) {
      Diamond* innerDiamond = dynamic_cast<Diamond*>(newSubformula.get());
      if (innerDiamond->getModality() == getModality()) {

          //RECURSIVELY SIMPLIFY THE RESULT
          return Diamond::create(getModality(),
            getPower() + innerDiamond->getPower(),
            innerDiamond->getSubformula(),
            getIsS5Mode()
          )->simplify();
      }
  }
  
  if (newSubformula != subformula_) {
      return Diamond::create(getModality(), getPower(), newSubformula, getIsS5Mode());
  }
  return shared_from_this();
}

shared_ptr<Formula> Diamond::modalFlatten() {
  subformula_ = subformula_->modalFlatten();
  if (subformula_->getType() == FDiamond) {
    Diamond *d = dynamic_cast<Diamond *>(subformula_.get());
    if (d->getModality() == modality_) {
      power_ += d->getPower();
      subformula_ = d->getSubformula();
    }
  }
  return shared_from_this();
}

shared_ptr<Formula> Diamond::axiomSimplify(int axiom, int depth) { 
    if (axiom == 2 && depth >= 1) {
        if (subformula_->getType() == FBox) {
            Box *b = dynamic_cast<Box *>(subformula_.get());
            return b->getSubformula()->axiomSimplify(axiom, depth);
        }
        return shared_from_this();
    } else {
        subformula_ = subformula_->axiomSimplify(axiom, depth+power_);
        if (depth > 0)
            power_ = 1;
        else
            power_ = min(power_, 2);
        return shared_from_this(); 
    }
}

shared_ptr<Formula> Diamond::create(int modality, int power,
                                    shared_ptr<Formula> subformula) {
  if (power == 0) {
    return subformula;
  }
  return shared_ptr<Formula>(new Diamond(modality, power, subformula));
}

shared_ptr<Formula> Diamond::create(vector<int> modality,
                                    const shared_ptr<Formula> &subformula) {
  if (modality.size() == 0) {
    return subformula;
  }
  shared_ptr<Formula> formula =
      Diamond::create(modality[modality.size() - 1], 1, subformula);
  for (size_t i = modality.size() - 1; i > 0; i--) {
    formula = Diamond::create(modality[i - 1], 1, formula);
  }
  return formula;
}

//CREATES S5 DIAMOND IF NECESSARY
shared_ptr<Formula> Diamond::create(int modality, int power,
                                    shared_ptr<Formula> subformula, bool isS5) {
  if (power == 0) {
    return subformula;
  }
  return shared_ptr<Formula>(new Diamond(modality, power, subformula, isS5));
}

//CREATES S5 DIAMOND IF NECESSARY
shared_ptr<Formula> Diamond::create(vector<int> modality,
                                    const shared_ptr<Formula> &subformula, bool isS5) {
  if (modality.size() == 0) {
    return subformula;
  }
  shared_ptr<Formula> formula =
      Diamond::create(modality[modality.size() - 1], 1, subformula, isS5);
  for (size_t i = modality.size() - 1; i > 0; i--) {
    formula = Diamond::create(modality[i - 1], 1, formula, isS5);
  }
  return formula;
}

//ADDED S5 INDICATOR HERE
shared_ptr<Formula> Diamond::constructDiamondReduced() const {
  return Diamond::create(modality_, power_ - 1, subformula_, getIsS5Mode());
}

//ADDED S5 INDICATOR HERE
shared_ptr<Formula> Diamond::clone() const {
  return create(modality_, power_, subformula_->clone(), getIsS5Mode());
}

//ADDED S5 INDICATOR HERE
bool Diamond::operator==(const Formula &other) const {
  if (other.getType() != getType()) {
    return false;
  }
  const Diamond *otherDiamond = dynamic_cast<const Diamond *>(&other);
  return modality_ == otherDiamond->modality_ &&
         power_ == otherDiamond->power_ &&
         *subformula_ == *(otherDiamond->subformula_) &&
         isS5Mode == otherDiamond->isS5Mode;
}

bool Diamond::operator!=(const Formula &other) const {
  return !(operator==(other));
}

size_t Diamond::hash() const {
  return diaHash_;
}